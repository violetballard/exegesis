## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for this re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Candidate range for integration: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`
- Scope classification: high-risk retrieval work because engine retrieval behavior and approved shared regression coverage are in scope.

## Scope Completed

This fixer regenerates the retrieval handoff around the actual current merge candidate and excludes off-lane packet-planner/tooling changes from retrieval integration. The merge candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints, keeping FTS cache/query snapshots deterministic, preserving basket-promotion references and provenance, and falling back from invalid direct context snapshots to canonical source/payload reconstruction.

## Canonical Demo Path

Advances: `retrieve relevant material`; `promote/gather context into basket` via deterministic FTS excerpt and provenance payloads. This lane keeps PageIndex and embeddings fallback-only and does not make them required retrieval paths.

## Tasks Completed

1. `retrieve relevant material`: normalize engine facade boolean constraints for `require_citations` and `prefer_exact_matches` without widening retrieval modes.
2. `retrieve relevant material`: keep FTS cache keys and retrieval source/query snapshots deterministic for repeated engine retrieval.
3. `promote/gather context into basket`: preserve basket-promotion item refs, item IDs, provenance, and sparse payload reconstruction from canonical FTS result data.
4. `retrieve relevant material`: harden generic context-bundle helper fallback from invalid direct context snapshots to canonical source/payload reconstruction.

## Merge Scope Accounting

Files in the current merge candidate (`main...HEAD`):

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

Explicitly excluded from this retrieval merge candidate:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

Those packet-planner/tooling paths are not present in `main...HEAD` for this branch and must not be reviewed or integrated as part of `feat-retrieval-fts`. If further planner/tooling work is needed, it should be submitted through the appropriate tooling/integrator path with explicit approval.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- Size: current merge candidate is `6 files changed, 215 insertions(+), 146 deletions(-)`.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Routing/provider impact: none.

## Roadmap/Vision

- Roadmap item affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capability affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 3 Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, 125 tests.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
