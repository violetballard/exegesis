## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for this re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Authoritative merge candidate before this packet-fix commit: `5a88788b77e5fa04eacd3f681047cfa72b4e6d37`
- Candidate range for implementation review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..5a88788b77e5fa04eacd3f681047cfa72b4e6d37`
- Scope classification: high-risk retrieval work because engine retrieval behavior and approved shared regression coverage are in scope.

## Scope Completed

This packet replaces the stale `adfa8cda` review boundary with the actual branch-tip implementation range. All commits in the candidate range that touch retrieval code or shared retrieval tests are implementation commits, including commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; they are not classified as metadata-only. The only metadata-only content in this handoff is packet documentation.

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

Files in the authoritative implementation candidate:

- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Retrieval implementation files in scope:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

Approved shared regression coverage in scope:

- `tests/unit/test_unified_retrieval.py`

Packet metadata updated by this fixer pass:

- `THREAD_PACKET.md`

Protected packet mirrors that could not be updated from this sandbox:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

Explicitly excluded from this retrieval merge candidate:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

Those packet-planner/tooling paths are not present in `main...HEAD` for this branch and must not be reviewed or integrated as part of `feat-retrieval-fts`. If further planner/tooling work is needed, it should be submitted through the appropriate tooling/integrator path with explicit approval.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- Size before this packet-fix commit: `6 files changed, 256 insertions(+), 112 deletions(-)` for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..5a88788b77e5fa04eacd3f681047cfa72b4e6d37`.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Routing/provider impact: none.

## Roadmap/Vision

- Roadmap item affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capability affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 3 Auditable generation.
- Canonical demo-path step made more real: `retrieve relevant material`, with basket/workflow promotion readiness through stable provenance and context refs.
- Proposed `README.md` patch text: none.

## Commands Run

Current fixer pass gate evidence:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, 125 tests.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
