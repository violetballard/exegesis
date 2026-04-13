## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet HEAD role: `review-packet correction for the actual committed tip`
- Current branch head before this fixer commit: `7668efb05966b8ee6eeeb2960a3862b005596a98`
- Reviewed implementation head: `7668efb05966b8ee6eeeb2960a3862b005596a98`
- Reviewed implementation range: `712714c24f92cdfe43f21127c2de1d4ea0bd2599..7668efb05966b8ee6eeeb2960a3862b005596a98`
- Handoff type: `shared/high-risk retrieval handoff regenerated against the actual committed branch tip`

## Packet HEAD context
- The actual committed branch tip before this fixer commit is `7668efb05966b8ee6eeeb2960a3862b005596a98`.
- `7668efb05966b8ee6eeeb2960a3862b005596a98` is an implementation commit, not a metadata-only packet refresh.
- The reviewed implementation commits in this regenerated slice are:
  - `3048d517` `Normalize retrieval query snapshots`
  - `fb2f0445` `feat-retrieval-fts: preserve sparse citation provenance`
  - `38074889` `Improve FTS cache key canonicalization`
  - `b9ead918` `feat(retrieval): enrich FTS evidence context`
  - `c558a819` `Normalize retrieval constraint booleans`
  - `d75472a6` `Fix FTS cache scope normalization`
  - `f54fdf6c` `Honor excerpt lookup confidentiality profiles`
  - `daeb0916` `Harden retrieval excerpt provenance normalization`
  - `8689af98` `Normalize canonical retrieval query whitespace`
  - `3b905670` `Add stable excerpt provenance fingerprints`
  - `1ac6ac38` `Normalize FTS cache query payloads`
  - `8284cdef` `Expose canonical retrieval rank fields`
  - `74d6c2f8` `feat(retrieval): stabilize excerpt lookup metadata`
  - `95610bda` `Tighten FTS excerpt payload normalization`
  - `7668efb0` `feat(retrieval): add excerpt lookup doc fingerprints`
- The docs-only alignment commits in this regenerated slice are:
  - `b008fe29` `docs(retrieval): refresh handoff traceability`
  - `c85b5f26` `docs(retrieval): finalize reviewer packet traceability`
  - `c6ab34e7` `docs(retrieval): regenerate packet for actual tip`
  - `da5e2db3` `fix(retrieval): correct reviewed tip packet role`
  - `249a0c50` `docs(retrieval): clarify canonical demo-path step`
  - `0cf508e5` `docs(retrieval): record canonical demo-path step`
  - `c163944c` `fix(retrieval): correct reviewed handoff packet tip`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Canonical demo-path step advanced
- `retrieve relevant material`
- This reviewed slice makes `retrieve relevant material` more real by keeping excerpt lookup, retrieval evidence, and downstream provenance on the authoritative FTS-first path with deterministic rank, fingerprint, and doc-identity fields.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- Retrieval query snapshots, scope and constraint normalization, and FTS cache keys are canonicalized so equivalent requests produce deterministic payloads, fingerprints, and cache reuse.
- Sparse citation, excerpt, and provenance reconstruction now rehydrates from canonical retrieval bundles with stable excerpt provenance fingerprints, confidentiality-aware excerpt lookup payloads, normalized lookup metadata, and doc-identity fingerprints.
- Retrieval evidence and top-level hit payloads now expose canonical rank-oriented fields needed for downstream engine flows without reintroducing PageIndex or embeddings as required paths.
- PageIndex and embeddings remain deferred compatibility strategies rather than required MVP paths.

## Reviewer fix reconciliation
- Required fix 1 is satisfied by anchoring the packet to the true reviewed implementation head `7668efb05966b8ee6eeeb2960a3862b005596a98` and the actual reviewed implementation range `712714c24f92cdfe43f21127c2de1d4ea0bd2599..7668efb05966b8ee6eeeb2960a3862b005596a98`.
- Required fix 2 is satisfied by removing the false metadata-only framing for the committed tip and aligning the traceability fields with git history.
- Required fix 3 is satisfied by listing the real files changed in the reviewed range and dropping stale packet-only framing from this handoff.
- Required fix 4 is satisfied by explicitly naming the canonical demo-path step advanced by this lane: `retrieve relevant material`.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Files changed

### Reviewed implementation files
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Docs-only alignment files inside the reviewed slice
- `THREAD_PACKET.md`

### Metadata-only handoff files edited in this fixer pass
- `THREAD_PACKET.md`

### Sandbox-blocked tracked packet files not editable in this environment
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Tasks completed
1. Normalized retrieval query, scope, date-range, and boolean constraint inputs so equivalent requests produce deterministic retrieval payloads and fingerprints.
2. Preserved sparse citation and excerpt provenance by rebuilding canonical retrieval bundles with stable excerpt provenance fingerprints, confidentiality-aware excerpt lookup payloads, and deterministic lookup metadata.
3. Canonicalized the FTS cache and evidence surfaces so equivalent requests reuse cached hits deterministically and expose stable shortlist, evidence, rank, and doc-identity fields for downstream consumers.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for payload normalization, provenance reconstruction, cache-key canonicalization, rank-field exposure, and excerpt lookup normalization.

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
