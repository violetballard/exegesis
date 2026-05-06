## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because this branch edits engine retrieval entrypoints/facades and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Authoritative reviewed implementation range for re-review: `378cf9a7..HEAD` on `codex/feat-retrieval-fts`.
- Evidence branch tip before this fixer commit: `e93e42766a...` (`fix(retrieval): make handoff packet authoritative`).
- Final HEAD SHA: reported in the final response after this fixer commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This packet supersedes earlier handoff packets for `codex/feat-retrieval-fts`. The only authoritative reviewed range is the full branch-tip range, `378cf9a7..HEAD`, at the time of re-review. Evidence below was generated from pre-fixer branch tip `e93e42766a...`; this fixer commit only updates handoff traceability metadata and the final SHA is reported with the fixer result.

Prior packet text incorrectly excluded code after `adfa8cd` and incorrectly implied that later packet-refresh commits were metadata-only. That claim is withdrawn. The reviewed range now includes every file changed from `378cf9a7` through the actual branch tip, including implementation commits such as `4f27cdc52ac52cb309afc950c807a66911e74da6` (`Harden retrieval identifier snapshots`) and the later packet correction commits on the branch.

The branch implements the FTS-first retrieval MVP path. SQLite FTS remains the deterministic retrieval source of truth. PageIndex and embeddings remain compatibility-only fallback shims that fail closed and are not reintroduced as required retrieval paths. The final work hardens stable retrieval identity by preserving ordered excerpt lookup fingerprints, document and excerpt provenance, sparse context payload snapshots, citations, basket summaries, and fail-closed compatibility behavior.

Canonical demo-path step advanced: `retrieve relevant material`. The work makes that step more real by constructing deterministic FTS-first queries, returning document and excerpt hits with stable provenance, reconstructing sparse payload snapshots, and exposing ordered excerpt lookup fingerprints alongside excerpt IDs, text hashes, citations, and basket item fingerprints. It also supports the next demo-path step, `promote or gather context into the basket`, because basket-facing summaries preserve auditable FTS lookup identity.

## Tasks Completed

1. Canonical FTS retrieval path: added and exported the canonical retrieval query constructor, `retrieve_auto` helper, and FTS-first service behavior through both retrieval facades.
2. Stable retrieval provenance: emitted deterministic document/excerpt hits, citations, basket summaries, primary lookup fingerprints, and ordered `excerpt_lookup_fingerprints` in manifests, summaries, evidence, and result fingerprint payloads.
3. Engine payload compatibility: normalized sparse retrieval source, summary, manifest, policy, provenance, excerpt identity, ordered identifier lists, and context payload snapshots for downstream engine flows.
4. Shared regression coverage: extended approved shared retrieval tests for facade exports, payload reconstruction, citation/provenance helpers, FTS-only excerpt backfill, lookup fingerprints, and fail-closed compatibility behavior.

## Files Changed

Authoritative reviewed implementation range for re-review: `378cf9a7..HEAD` on `codex/feat-retrieval-fts`.
Evidence range before this fixer commit: `378cf9a7..e93e42766a...`

- `.codex/kickoff_packets/feat-retrieval-fts.md` - lane kickoff metadata corrected during earlier packet refreshes.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata corrected during earlier packet refreshes.
- `THREAD_PACKET.md` - authoritative handoff packet for branch-tip review.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy integration behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic retrieval payload and sparse snapshot normalization.
- `src/qual/retrieval/__init__.py` - retrieval facade exports.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service, provenance, citation, and lookup fingerprint behavior.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the retrieval contract.

Integrator-locked files: none.
Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Diff Evidence

Command: `git diff --stat 378cf9a7..HEAD` at pre-fixer tip `e93e42766a...`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 +++-
 THREAD_PACKET.md                             |  189 ++---
 src/qual/engine/retrieval/__init__.py        |   63 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1013 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  679 +++++++++++++++--
 tests/unit/test_unified_retrieval.py         |  912 ++++++++++++++++++++++-
 9 files changed, 2783 insertions(+), 334 deletions(-)
```

Command: `git diff --name-status 378cf9a7..HEAD` at pre-fixer tip `e93e42766a...`

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
- Size accounting for authoritative reviewed implementation range at pre-fixer evidence tip: `2783 insertions(+), 334 deletions(-)`.
- AGENTS high-risk file/size status: exceeds `<=8 files` and `<=300 net LOC`.
- Integrator exception status: explicit high-risk size/file exception is required for approval of this branch-tip range. This packet does not claim high-risk size compliance.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Packet-only fixer impact: corrects handoff range, false metadata-only traceability, budget accounting, files changed, canonical demo-path mapping, and gate reporting for re-review.
- Remaining risk: integration approval depends on accepting the documented high-risk size/file-count exception or requesting a split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS excerpt lookup identities alongside promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 144 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 144 unit tests.

## Risks/Blockers

No implementation blocker is known. The branch-tip review range is now explicit and complete. Approval requires the integrator to accept the documented high-risk budget exception because the actual reviewed range exceeds the AGENTS high-risk file and LOC limits.
