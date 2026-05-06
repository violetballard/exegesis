## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Authoritative reviewed implementation range for re-review: `378cf9a7..HEAD` on `codex/feat-retrieval-fts`.
- Implementation branch tip before this fixer commit: `58917e11fae870acee14ac876888a0b15e6c0094`.
- Final HEAD SHA: reported in the final response after this fixer commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. The only authoritative reviewed range is the full branch-tip range, `378cf9a7..HEAD`, at the time of re-review. Evidence below was regenerated from branch tip `58917e11fae870acee14ac876888a0b15e6c0094`; this fixer commit refreshes handoff traceability without narrowing the reviewed implementation range. The final SHA is reported with the fixer result.

Prior packet text incorrectly excluded code after `adfa8cd` and incorrectly implied that later packet-refresh commits were metadata-only. That claim is withdrawn. The reviewed range now includes every file changed from `378cf9a7` through the actual branch tip, including implementation commits such as `4ca1c6b0c8e6bd1bbf2fb27ec3ed5f60729bac52` (`Harden sparse retrieval citation rehydration`, which changes `src/qual/engine/retrieval/payload.py`) and `fa14772592bba8a097f802fd4376aba9ab329e1c` (`fix(retrieval): surface candidate resolution provenance`, which changes `src/qual/retrieval/service.py`), plus branch-tip packet refresh commit `0940be225ea4c80cc5f1fdc27b82a6cb4c60d024`.

Out-of-lane packet tooling scope: `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not part of this retrieval handoff. They appear in older cumulative accounting from `d7fd5d2..adfa8cd`, but the regenerated authoritative review range is `378cf9a7..HEAD`; `git diff --name-status 378cf9a7..HEAD` does not include either file. This retrieval handoff requests review only for the files listed below.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The final work hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, candidate-resolution snapshots, top-level context query/policy/manifest/summary snapshots, direct excerpt lookup audit identity, and fail-closed compatibility behavior.

Canonical demo-path step advanced: `retrieve relevant material`. The work makes that step more real by constructing deterministic FTS-first queries, returning document and excerpt hits with stable provenance, reconstructing sparse payload snapshots, and exposing ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, candidate-resolution snapshots, and basket item fingerprints. It also supports the next demo-path step, `promote or gather context into the basket`, because basket-facing summaries preserve auditable FTS lookup identity and candidate-set provenance.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
   Canonical demo-path step advanced: `retrieve relevant material`.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, candidate-resolution snapshots, primary lookup fingerprints, ordered `excerpt_lookup_fingerprints`, and direct excerpt lookup audit identity in manifests, summaries, evidence, audit events, and result fingerprint payloads.
   Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket` by preserving promotion-ready provenance.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, and context payload snapshots for downstream engine flows, including top-level context bundle query, policy, manifest, summary, and citation status fields.
   Canonical demo-path step advanced: `retrieve relevant material`.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, and fail-closed compatibility behavior.
   Canonical demo-path step advanced: `retrieve relevant material`.

AGENTS.md narrowing statement: this work makes the `retrieve relevant material` step more real by ensuring engine retrieval uses FTS-only excerpt lookup with deterministic provenance suitable for basket promotion.

## Files Changed

Authoritative reviewed implementation range for re-review: `378cf9a7..HEAD` on `codex/feat-retrieval-fts`.
Evidence stats below were regenerated from `378cf9a7` with this fixer pass included before commit.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during earlier packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during earlier packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload, sparse snapshot normalization, and top-level context bundle reconstruction.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, candidate-resolution citation snapshots, lookup fingerprint behavior, direct excerpt lookup audit identity, and context bundle packaging.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract, direct excerpt lookup audit identity, and context bundle copy safety.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The `.codex/` directory in this worktree is currently protected from writes by the local filesystem (`Operation not permitted` on creating or rewriting files under `.codex/`), so stale `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` text should not be used as the review source of truth for this pass.

## Diff Evidence

Command: `git diff --stat 378cf9a7..HEAD`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  200 +++--
 src/qual/engine/retrieval/__init__.py        |   63 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1145 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  694 ++++++++++++++--
 tests/unit/test_unified_retrieval.py         |  955 ++++++++++++++++++++++-
 9 files changed, 2970 insertions(+), 348 deletions(-)
```

Command: `git diff --name-status 378cf9a7..HEAD`

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
- File count for authoritative reviewed implementation range: `9 files changed`.
- Size accounting for authoritative reviewed implementation range: `2970 insertions(+), 348 deletions(-)`.
- AGENTS high-risk file/size status: exceeds `<=8 files` and `<=300 net LOC`.
- Integrator exception status: explicit high-risk size/file exception is required for approval of this branch-tip range. This packet does not claim high-risk size compliance.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Current fixer impact: records direct excerpt lookup audit identity while preserving FTS-only lookup behavior, then refreshes handoff range, budget accounting, files changed, canonical demo-path mapping, and gate reporting for re-review against the actual branch tip.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities, direct context-bundle retrieval snapshots, and promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because pytest is not installed in this environment (`No module named pytest`).
- `python -m unittest tests.unit.test_unified_retrieval` - passed 76 focused retrieval tests.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; no branch policy was configured, so scope-check reported skip then pass.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 145 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 145 unit tests.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete. Approval requires the integrator to accept the documented high-risk budget exception because the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
