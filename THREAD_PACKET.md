## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval feature handoff for the FTS-first retrieval lane.
- Scope classification: high-risk because the reviewed branch-tip source/test delta includes the approved shared-by-approval regression file `tests/unit/test_unified_retrieval.py`.
- Review boundary for this handoff: `378cf9a74a3658058079a32f186fcd254c4a4034..ed0cc8037310156946229a7ac161400f43aba7fb` for source/test implementation, plus the final packet-only fixer commit reported in the final handoff.
- Source/test implementation head: `ed0cc8037310156946229a7ac161400f43aba7fb`.
- Final HEAD SHA: reported in the final fixer response after the packet-only commit is created.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane. No integrator-locked files are edited in this handoff.

## Scope Completed

This handoff covers the actual branch-tip retrieval implementation delta through `ed0cc8037310156946229a7ac161400f43aba7fb`; no commit in that reviewed source/test range is being represented as metadata-only. The cumulative FTS-first retrieval work keeps SQLite FTS authoritative, exports the canonical retrieval helpers through the retrieval facades, normalizes retrieval payloads and provenance snapshots for downstream engine flows, reconstructs sparse source/context/citation bundles deterministically, and exposes basket promotion readiness, IDs, fingerprints, counts, and references in retrieval payloads and citation snapshots. PageIndex and embeddings remain deferred compatibility metadata/fallback shims and are not active retrieval requirements.

Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. The actual reviewed delta supports Milestone 3 FTS-first structured retrieval by making FTS excerpts and citation bundles sufficient for deterministic basket/workflow promotion without rehydrating non-FTS retrieval paths.

## Tasks Completed

1. Canonical step `retrieve relevant material`: Made SQLite FTS the authoritative retrieval path, including FTS-only excerpt lookup, cache invalidation/scoping, query normalization, date/scope/doc-type constraint normalization, and fail-closed handling for unresolved or non-FTS scopes.
2. Canonical step `retrieve relevant material`: Stabilized retrieval payloads, source bundles, context bundles, citation bundles, provenance fingerprints, excerpt lookup fingerprints, and evidence context so downstream engine flows receive deterministic structured snapshots.
3. Canonical step `promote or gather context into the basket`: Added deterministic basket promotion readiness/counts, basket item IDs, fingerprints, context references, source references, citation references, and promotion candidate reconstruction across direct retrieval results, sparse backfills, context bundles, and downstream payloads.
4. Shared regression coverage: Extended the approved shared-by-approval file `tests/unit/test_unified_retrieval.py` to cover the FTS-first retrieval contract, facade exports, fail-closed non-FTS behavior, deterministic payload/citation/provenance backfills, and basket/workflow promotion metadata.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md` - packet mirror present in the branch-tip delta; this sandbox cannot rewrite it because the `.codex` mirror path is protected by filesystem permissions.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata mirror present in the branch-tip delta; this sandbox cannot rewrite it because the `.codex` mirror path is protected by filesystem permissions.
- `THREAD_PACKET.md` - authoritative handoff packet regenerated for the actual branch-tip review boundary and required gate results.
- `src/qual/engine/retrieval/__init__.py` - exports canonical retrieval facade helpers used by engine-side retrieval flows.
- `src/qual/engine/retrieval/fts_strategy.py` - hardens FTS strategy hit snapshots and FTS-only retrieval behavior.
- `src/qual/engine/retrieval/payload.py` - normalizes retrieval payload/query/policy/provenance snapshots and basket promotion metadata for downstream consumers.
- `src/qual/retrieval/__init__.py` - exposes the canonical retrieval query and auto-retrieval helpers from the retrieval package.
- `src/qual/retrieval/service.py` - implements deterministic FTS retrieval, excerpt lookup, citation/source/context bundle backfills, provenance fingerprints, and basket promotion summary fields.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the FTS-first retrieval contract and basket promotion payload/citation behavior.

Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- Actual source/test implementation delta: `9 files changed, 2545 insertions(+), 260 deletions(-)` for `378cf9a74a3658058079a32f186fcd254c4a4034..ed0cc8037310156946229a7ac161400f43aba7fb`.
- AGENTS size/file status: the full branch-tip source/test delta exceeds the high-risk size guideline of `<=8 files` and `<=300 net LOC`.
- Approved exception status: the shared regression file `tests/unit/test_unified_retrieval.py` is approved for this retrieval lane; no separate size/LOC exception is recorded in this worktree packet.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain deferred compatibility metadata/fallback-only behavior; no active non-FTS retrieval path is introduced.
- Remaining risk: review should explicitly account for the size/LOC overage. The implementation scope remains inside retrieval-owned paths plus the approved shared regression file.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 real workflow loop, specifically FTS-first structured retrieval and basket/workflow promotion support; Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-first context handling and auditable state/workflow.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by surfacing stable FTS evidence, source identity, citation identity, and promotion-ready basket references.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed; output reported no policy for branch `codex/feat-retrieval-fts`, skipped policy enforcement, and passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke plus 144 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke, and 144 unit tests.

## Risks/Blockers

The authoritative mutable packet now uses one review boundary and does not rely on metadata-only wording for commits that touched retrieval code. The `.codex` packet mirror files could not be rewritten in this sandbox: `apply_patch` rejected those paths as outside the writable project, and a direct open failed with `PermissionError: [Errno 1] Operation not permitted`. Treat `THREAD_PACKET.md` as the corrected handoff source of truth for this fixer pass.

The remaining recorded risk is budget accounting: the branch-tip source/test delta exceeds the AGENTS high-risk file and LOC guidelines, and this packet records that no separate size/LOC exception is present beyond the approved shared regression file.

Final canonical demo-path statement: this work keeps SQLite FTS as the deterministic retrieval source of truth while making structured retrieval snapshots sufficient to audit basket promotion readiness and stable retrieved-item identity for downstream revise, patch, and apply flows.
