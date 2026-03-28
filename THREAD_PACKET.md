## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`
- Handoff type: packet correction only; this commit updates handoff metadata, not retrieval code.

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so generation flows receive deterministic excerpt payloads and provenance, matching PRODUCT_VISION.md capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow. PageIndex and embeddings remain deferred as fallback-only plumbing, and this packet correction stays limited to metadata for the retrieval-owned feature surface.

## Files changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Tasks completed

1. Canonicalized FTS excerpt lookup so excerpt rehydration returns deterministic payloads and records an audit trail.
2. Normalized retrieval provenance and downstream payload builders so excerpt, source, citation, doc, and context bundles share stable hashes and fingerprints.
3. Locked the retrieval policy to FTS-first and kept PageIndex/embeddings deferred as fallback-only plumbing.
4. Exposed the canonical retrieval entrypoints through the engine/package facades so the FTS-first path remains the stable default.

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `LOW`
- Blockers: none

## Roadmap item(s) affected

- ROADMAP.md: Milestone 4: Retrieval Layer (Planned)

## Vision capability affected

- PRODUCT_VISION.md: 2. Retrieval-first context handling
- PRODUCT_VISION.md: 6. Auditable state and workflow

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
