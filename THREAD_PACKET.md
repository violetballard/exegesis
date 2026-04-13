## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Current branch head before this fixer commit: `380748890f6b79e9f5eb0e6842018d7d36a4b492`
- Reviewed implementation head: `380748890f6b79e9f5eb0e6842018d7d36a4b492`
- Reviewed implementation range: `712714c24f92cdfe43f21127c2de1d4ea0bd2599..380748890f6b79e9f5eb0e6842018d7d36a4b492`
- Handoff type: `shared/high-risk retrieval handoff regenerated against the actual branch tip`

## Packet HEAD context
- The actual branch tip before this fixer commit is `380748890f6b79e9f5eb0e6842018d7d36a4b492`.
- `380748890f6b79e9f5eb0e6842018d7d36a4b492` is an implementation commit, not a metadata-only packet refresh.
- The reviewed implementation commits in this regenerated slice are:
  - `3048d517` `Normalize retrieval query snapshots`
  - `fb2f0445` `feat-retrieval-fts: preserve sparse citation provenance`
  - `38074889` `Improve FTS cache key canonicalization`
- The docs-only alignment commits in this regenerated slice are:
  - `b008fe29` `docs(retrieval): refresh handoff traceability`
  - `c85b5f26` `docs(retrieval): finalize reviewer packet traceability`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping SQLite FTS authoritative while hardening deterministic retrieval payloads, preserving sparse citation/provenance reconstruction, and making the one-entry FTS cache reuse semantically equivalent retrieval requests instead of re-running identical SQLite work.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- Retrieval query snapshots and downstream payloads are normalized so semantically equivalent query text and scope inputs produce deterministic source bundles and fingerprints.
- Sparse citation and provenance payload reconstruction now rehydrates from canonical retrieval bundles instead of silently dropping citation context.
- The FTS strategy cache key is canonicalized across equivalent query objects and candidate doc ID order, and uncached reads still refresh the one-slot cache for later deterministic reuse.
- PageIndex and embeddings remain deferred compatibility strategies rather than required MVP paths.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by anchoring the packet to the true reviewed implementation head `380748890f6b79e9f5eb0e6842018d7d36a4b492` and the actual reviewed implementation range `712714c24f92cdfe43f21127c2de1d4ea0bd2599..380748890f6b79e9f5eb0e6842018d7d36a4b492`.
- Required fix 2 is satisfied by replacing the false metadata-only description of `380748890f6b79e9f5eb0e6842018d7d36a4b492` with its real retrieval scope.
- Required fix 3 is satisfied by re-running and recording the required local gates for the actual reviewed tip.
- Required fix 4 is satisfied by explicitly naming the canonical demo-path step advanced by this lane: `retrieve relevant material`.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Files changed

### Reviewed implementation files
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Docs-only alignment files inside the reviewed slice
- `THREAD_PACKET.md`

### Metadata-only handoff files edited in this fixer pass
- `THREAD_PACKET.md`

## Tasks completed
1. Normalized retrieval query snapshots so equivalent query text and scope inputs produce deterministic retrieval payloads.
2. Preserved sparse citation provenance by rebuilding citation/provenance structures from canonical retrieval bundles when top-level payloads are incomplete.
3. Canonicalized the FTS one-slot cache key and refresh behavior so equivalent requests reuse cached hits deterministically without introducing alternate required retrieval paths.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for payload normalization, sparse citation/provenance reconstruction, and FTS cache-key canonicalization.

## Budget alignment
- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The reviewed implementation slice stays within lane-owned retrieval paths plus the approved shared regression file.
- No integrator-locked files were edited in the reviewed implementation slice.

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risk: `HIGH`
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`

## Vision capability affected
- `2. Retrieval-first context handling`
- `3. Canonical engine contract`
- `6. Auditable state and workflow`

## Routing/provider impact note
- None

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only)
