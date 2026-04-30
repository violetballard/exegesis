## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for this re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Current branch tip before this fixer packet commit: `871f69bfb`
- Authoritative reviewed branch range before this fixer packet commit: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..871f69bfb`
- Authoritative reviewed implementation head: `5a88788b77e5fa04eacd3f681047cfa72b4e6d37`
- Authoritative reviewed implementation range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..5a88788b77e5fa04eacd3f681047cfa72b4e6d37`
- Commits after the implementation head are packet metadata only: `6c4beb2ef`, `dd22dfdb9`, `877367dca`, `80e6c6f32`, and `871f69bfb` each modify only `THREAD_PACKET.md` and contain no source or test implementation changes.
- Scope classification: high-risk retrieval work because approved shared regression coverage is in scope.

## Scope Completed

This packet chooses one review scope and replaces the stale `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca` review boundaries with one authoritative current implementation range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..5a88788b77e5fa04eacd3f681047cfa72b4e6d37`. Within the current branch range before this fixer packet commit, every non-metadata source or test change intended to merge is contained in that implementation range. The later commits `6c4beb2ef`, `dd22dfdb9`, `877367dca`, `80e6c6f32`, and `871f69bfb` are explicitly excluded from implementation review because `git log --name-only 5a88788b77e5fa04eacd3f681047cfa72b4e6d37..871f69bfb` shows only `THREAD_PACKET.md`. The older cumulative boundary `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca` is historical only and is not requested for this re-review. The commit `5a88788b77e5fa04eacd3f681047cfa72b4e6d37` is explicitly an implementation commit because it normalizes `RetrievalQuery.query_text` and `scope` snapshots in `src/qual/retrieval/service.py`.

The merge candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints and required query text/scope snapshots, keeping FTS cache and query snapshots deterministic, preserving basket-promotion references and provenance, invalidating stale FTS cache state on document updates, and falling back from invalid direct context snapshots to canonical source/payload reconstruction.

## Canonical Demo Path

Advances the canonical retrieval step: `retrieve relevant material`.

Basket/workflow promotion readiness: retrieval output now carries deterministic excerpt payloads, provenance fingerprints, source/context bundle refs, basket-promotion item refs, item IDs, and citation metadata so downstream workflow promotion can gather the same retrieved material into a basket without depending on PageIndex-only or embedding-only paths.

## Tasks Completed

1. `retrieve relevant material`: normalize engine facade query constraints, boolean flags, date ranges, doc types, required query text/scope snapshots, and cache keys so repeated FTS retrieval is deterministic.
2. `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, reject non-FTS excerpt normalization, preserve ranked IDs, document identities, confidentiality profiles, section hints, and excerpt provenance.
3. `promote/gather context into basket`: preserve basket-promotion refs, item IDs, citation refs, provenance fingerprints, and source/context bundles during sparse payload and context-bundle reconstruction.
4. `retrieve relevant material`: harden cache invalidation and fallback reconstruction for document updates, sparse direct context snapshots, and generic context-bundle helpers while keeping PageIndex and embeddings fallback-only.

## Merge Scope Accounting

Files in the authoritative current branch range:

- `THREAD_PACKET.md` - packet metadata; out-of-lane handoff documentation required by `INTEGRATION.md`.
- `src/qual/engine/retrieval/__init__.py` - lane-owned via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/fts_strategy.py` - lane-owned via `src/qual/engine/retrieval/**`.
- `src/qual/engine/retrieval/payload.py` - lane-owned via `src/qual/engine/retrieval/**`.
- `src/qual/retrieval/service.py` - lane-owned via `src/qual/retrieval/**`.
- `tests/unit/test_unified_retrieval.py` - shared-by-approval regression coverage for the canonical retrieval contract.

Non-metadata source/test implementation files in `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..80e6c6f32db8cd541fd4f06bcec1ebf6066114c4`:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Protected packet mirrors that remain stale because this sandbox rejected writes to them:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

Treat `THREAD_PACKET.md` as the corrected handoff packet for this re-review. Those mirror files still contain historical ranges and are not the authoritative packet for this fixer pass.

Integrator-locked files: none.

Out-of-scope files not present in the authoritative reviewed implementation range:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`

Those paths are not present in `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..5a88788b77e5fa04eacd3f681047cfa72b4e6d37` and must not be reviewed or integrated as part of this `feat-retrieval-fts` handoff.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- Size for authoritative reviewed implementation range: `6 files changed, 256 insertions(+), 112 deletions(-)`.
- File budget: `6/8` high-risk files.
- Net LOC budget: `+144/300` high-risk net LOC.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Integrator-locked files: none.
- Routing/provider impact: none.
- Approval note: shared regression coverage in `tests/unit/test_unified_retrieval.py` is approved for this lane and applies to the full authoritative reviewed implementation range `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..5a88788b77e5fa04eacd3f681047cfa72b4e6d37` because it exercises the canonical retrieval contract. The packet metadata file is required handoff documentation, not runtime scope.

## Roadmap/Vision

- Roadmap item affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capability affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 6 Auditable state and workflow.
- Canonical demo-path step made more real: `retrieve relevant material`.
- Canonical demo-path basket step made more real where structured payloads support it: `promote or gather context into the basket`, through stable provenance, source/context refs, citation refs, basket-promotion item refs, and deterministic payload reconstruction.
- Proposed `README.md` patch text: none.

## Commands Run

Current fixer pass gate evidence:

- Gates below were re-run after the reviewer-required packet scope and demo-path corrections were verified in `THREAD_PACKET.md`.
- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, 125 tests.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
