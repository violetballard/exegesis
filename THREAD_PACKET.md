## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`
- Handoff type: retrieval feature handoff; this packet records the lane-owned implementation scope and required gate results.

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so generation flows receive deterministic excerpt payloads and provenance, matching PRODUCT_VISION.md capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow. PageIndex and embeddings remain deferred as fallback-only plumbing, and the handoff stays limited to the retrieval-owned feature surface. Packet/planner tooling artifacts are excluded from the feature file list.

## Files changed

- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/policy.py`

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

## Handoff correction note

- This packet correction aligns the metadata with the retrieval implementation and removes the packet/tooling scope contradiction from the reviewed handoff.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
- Feature handoff scope is lane-contained; packet/planner tooling artifacts are not part of the feature file list.
