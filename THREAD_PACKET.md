## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because the actual branch-tip implementation range edits approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and engine retrieval entrypoint/facade code.
- Reviewed merge-candidate range before this final fixer commit: `9511a016c20f09b43c6e7a571e0a8a49f90ea209..0d6b774afb809783a4e3375c06e51b6a557bcfd2`
- Reviewed branch tip before this final fixer commit: `0d6b774afb809783a4e3375c06e51b6a557bcfd2`
- Final HEAD SHA: reported in the final response after this fixer commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This branch-tip handoff covers the complete FTS-first retrieval implementation currently on `codex/feat-retrieval-fts`, including the source and test changes that earlier packets incorrectly excluded after `adfa8cd`. SQLite FTS remains the deterministic retrieval source of truth; PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths.

This final fixer pass keeps the same FTS-first scope and hardens ordered retrieval identifier snapshots so manifest and summary fingerprint lists only expose present FTS provenance values, keeping sparse or partial downstream context bundles free of placeholder `None` entries.

Canonical demo-path mapping:

- `retrieve relevant material`: the retrieval service constructs deterministic FTS-first queries, returns document and excerpt hits with stable provenance, reconstructs sparse payload snapshots, and exposes ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, and basket item fingerprints.
- `promote or gather context into the basket`: retrieval evidence and basket-facing summaries preserve stable lookup identity so downstream revise, patch, and apply flows can audit promoted FTS material without rehydrating PageIndex or embeddings.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, primary lookup fingerprints, and ordered `excerpt_lookup_fingerprints` in manifests, summaries, evidence, and result fingerprint payloads.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, and context payload snapshots for downstream engine flows.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, and fail-closed compatibility behavior.

## Files Changed

Reviewed range before this packet-refresh fixer commit `9511a016c20f09b43c6e7a571e0a8a49f90ea209..0d6b774afb809783a4e3375c06e51b6a557bcfd2`:

- `THREAD_PACKET.md` - authoritative handoff packet for this branch-tip review.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload and sparse snapshot normalization.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, citation, and lookup fingerprint behavior.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Diff Evidence

Command: `git diff --stat 9511a016c20f09b43c6e7a571e0a8a49f90ea209..0d6b774afb809783a4e3375c06e51b6a557bcfd2`

```text
 THREAD_PACKET.md                     | 208 +++++++++++-------------------
 src/qual/engine/retrieval/payload.py | 240 +++++++++++++++++++++++++++--------
 src/qual/retrieval/service.py        |  57 +++++++++
 tests/unit/test_unified_retrieval.py | 198 +++++++++++++++++++++++++++++
 4 files changed, 515 insertions(+), 188 deletions(-)
```

Command: `git diff --name-status 9511a016c20f09b43c6e7a571e0a8a49f90ea209..0d6b774afb809783a4e3375c06e51b6a557bcfd2`

```text
M	THREAD_PACKET.md
M	src/qual/engine/retrieval/payload.py
M	src/qual/retrieval/service.py
M	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- Size accounting for reviewed merge-candidate range before this final fixer commit: `4 files changed, 515 insertions(+), 188 deletions(-)`.
- AGENTS high-risk size/file status: exceeds `<=300 net LOC`.
- Integrator exception status: explicit size exception is required for approval of this branch-tip range. This packet no longer claims high-risk size compliance.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Final fixer impact: no routing/provider changes; only present-value compaction for ordered retrieval identifier lists plus packet metadata.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context and auditable state/workflow.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities alongside promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 75 retrieval unit tests before this final fixer edit.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 75 retrieval unit tests after this final fixer edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `python -m pytest tests/unit/test_unified_retrieval.py` - not run; current interpreter has no `pytest` module.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 75 retrieval unit tests.
- `./quality-test.sh` - passed smoke tests and 144 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 144 unit tests.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete. Approval requires the integrator to accept the documented high-risk budget exception because the actual reviewed range exceeds the AGENTS high-risk LOC limit.
