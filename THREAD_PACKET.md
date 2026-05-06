## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because the actual branch-tip implementation range edits approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and engine retrieval entrypoint/facade code.
- Reviewed implementation range: `378cf9a..27323962b4c6b627ecb78ac2b3da0bebe071a309`
- Reviewed implementation head: `27323962b4c6b627ecb78ac2b3da0bebe071a309`
- Final HEAD SHA: reported in the final response after this fixer commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This branch-tip handoff covers the complete FTS-first retrieval implementation currently on `codex/feat-retrieval-fts`, including the source and test changes that earlier packets incorrectly excluded after `adfa8cd`. SQLite FTS remains the deterministic retrieval source of truth; PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths.

Canonical demo-path mapping:

- `retrieve relevant material`: the retrieval service constructs deterministic FTS-first queries, returns document and excerpt hits with stable provenance, reconstructs sparse payload snapshots, and exposes ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, and basket item fingerprints.
- `promote or gather context into the basket`: retrieval evidence and basket-facing summaries preserve stable lookup identity so downstream revise, patch, and apply flows can audit promoted FTS material without rehydrating PageIndex or embeddings.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, primary lookup fingerprints, and ordered `excerpt_lookup_fingerprints` in manifests, summaries, evidence, and result fingerprint payloads.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, and context payload snapshots for downstream engine flows.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, and fail-closed compatibility behavior.

## Files Changed

Reviewed range `378cf9a..27323962b4c6b627ecb78ac2b3da0bebe071a309`:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff packet metadata for the retrieval handoff.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata consumed by packet automation.
- `THREAD_PACKET.md` - authoritative handoff packet for this branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports for canonical retrieval helpers.
- `src/qual/engine/retrieval/fts_strategy.py` - engine-side FTS strategy behavior and fallback boundaries.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload and sparse snapshot normalization.
- `src/qual/retrieval/__init__.py` - public retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, citation, and lookup fingerprint behavior.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Diff Evidence

Command: `git diff --stat 378cf9a..27323962b4c6b627ecb78ac2b3da0bebe071a309`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |  36 +-
 .codex/lane_meta/feat-retrieval-fts.json     | 155 ++++-
 THREAD_PACKET.md                             | 112 ++--
 src/qual/engine/retrieval/__init__.py        |  63 +-
 src/qual/engine/retrieval/fts_strategy.py    |  59 +-
 src/qual/engine/retrieval/payload.py         | 894 ++++++++++++++++++++++++--
 src/qual/retrieval/__init__.py               |  11 +
 src/qual/retrieval/service.py                | 608 ++++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 912 ++++++++++++++++++++++++++-
 9 files changed, 2590 insertions(+), 260 deletions(-)
```

Command: `git diff --name-status 378cf9a..27323962b4c6b627ecb78ac2b3da0bebe071a309`

```text
M	.codex/kickoff_packets/feat-retrieval-fts.md
M	.codex/lane_meta/feat-retrieval-fts.json
M	THREAD_PACKET.md
M	src/qual/engine/retrieval/__init__.py
M	src/qual/engine/retrieval/fts_strategy.py
M	src/qual/engine/retrieval/payload.py
M	src/qual/retrieval/__init__.py
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- Size accounting for reviewed implementation range: `9 files changed, 2590 insertions(+), 260 deletions(-)`.
- AGENTS high-risk size/file status: exceeds `<=8 files` and `<=300 net LOC`.
- Integrator exception status: explicit size/file-count exception is required for approval of this branch-tip range. This packet no longer claims high-risk budget compliance.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context and auditable state/workflow.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities alongside promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; repo policy reported no branch-specific policy before passing.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 144 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 144 unit tests.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete. Approval requires the integrator to accept the documented high-risk budget exception because the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
