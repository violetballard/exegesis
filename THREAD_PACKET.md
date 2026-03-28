## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`
  - `addc72aead4d458748f06497865deef9ab54db26`
  - `a7b2bba6a338d823519701cc38a30d10f819aa7b`
  - `c4944661a0a682821c486810918c2c1fabac1a41`

## Scope completed

The lane tightened the FTS-first retrieval MVP so source-bundle snapshots can rehydrate the canonical retrieval context deterministically, while excerpt payloads and provenance remain stable and auditable. PageIndex and embeddings stay deferred as fallback-only plumbing, and this handoff remains limited to the retrieval-owned feature surface through the current HEAD commit.

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

- ROADMAP.md: MVP Focus Through 2026-05-04 -> `feat-retrieval-fts`

## Vision capability affected

- 2. Retrieval-first context handling
- 3. Auditable generation

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
