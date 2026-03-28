## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`
  - `addc72aead4d458748f06497865deef9ab54db26`
  - `a7b2bba6a338d823519701cc38a30d10f819aa7b`
  - `c4944661a0a682821c486810918c2c1fabac1a41`
  - `827d1d25d4a707f2efa678a83c7de087ebd5fc0c`

## Scope completed

This handoff covers the source-bundle context regression at the current HEAD: source-bundle snapshots can rehydrate canonical retrieval context deterministically, excerpt payloads and provenance stay stable and auditable, and PageIndex plus embeddings remain deferred as fallback-only plumbing. This maps to `docs/TASKS.md` (`feat-retrieval-fts`) and `ROADMAP.md` (Milestone 3: Real workflow loop), and the handoff stays limited to the retrieval-owned feature surface.

## Files changed

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

## Tasks completed

1. Added the excerpt lookup audit trail and deterministic rehydration path in the retrieval service.
2. Canonicalized excerpt provenance so downstream payloads carry stable hashes and fingerprints.
3. Accepted source-bundle context fallbacks in the engine payload helpers without widening the retrieval policy.
4. Added a regression test that exercises the source-bundle-only context reconstruction path and verifies snapshot safety.

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

- `docs/TASKS.md`: `feat-retrieval-fts` -> keep the FTS-first retrieval path authoritative; expose retrieval through the canonical engine contract; keep structured results suitable for workflow cards and basket promotion
- `ROADMAP.md`: Milestone 3: Real workflow loop

## Vision capability affected

- 2. Retrieval-first context handling
- 3. Auditable generation

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
