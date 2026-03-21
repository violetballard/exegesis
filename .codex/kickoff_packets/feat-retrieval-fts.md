# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Handoff alignment commit: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Reviewed commit type: Docs-only handoff alignment; no retrieval code changes in this commit.

## Scope completed

This commit updates only the handoff artifacts in lane-owned docs paths. The completed scope is the three packet files: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, and `THREAD_PACKET.md`. It records that the reviewed retrieval implementation lives in `36893f06df85409c4595d64adb8af60455c086a6`, that the deferred-policy boundary lives in `dc8f79e4abeb30de51854fdd84d35b97993955b8`, and that `203906231e9c47371b6d7bc4028bc4f60e764581` does not add retrieval code changes. The handoff keeps the file list restricted to those docs files, states the owned retrieval behavior as FTS-first for `vault`, `collection:`, and `doc:` scopes, and documents `section:` as a compatibility break in the current MVP until fallback support exists. `src/qual/engine/tools/retrieval_tools.py` is not included in the handoff surface. PageIndex and embeddings references remain deferred-only history, and the roadmap/vision mapping stays scoped to the docs-only handoff boundary rather than claiming feature delivery in this commit.

### Prior commit references (reference only)
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

### Cleanup boundary note
- `src/qual/engine/retrieval/policy.py`

### Code-diff evidence
- `.codex/kickoff_packets/feat-retrieval-fts.md`: re-anchors the handoff metadata to the actual commit boundary.
- `.codex/lane_meta/feat-retrieval-fts.json`: mirrors the same scope and file-list correction in structured form.
- `THREAD_PACKET.md`: records the docs-only nature of this commit and the earlier implementation/cleanup commits it points to.
- Roadmap/vision mapping: documents the Milestone 4 retrieval boundary that this handoff references, without asserting new retrieval behavior in this commit.

### Priority outcomes
1. State clearly that `203906231e9c47371b6d7bc4028bc4f60e764581` is a docs-only cleanup commit.
2. Keep the file list aligned with the docs-only diff and separate earlier implementation files from the handoff artifacts.
3. Treat PageIndex and embeddings mentions as deferred markers only, not active MVP paths.
4. Make the roadmap and vision fields read as handoff-boundary documentation, not feature delivery.

### Tasks
1. Re-anchor the packet to the actual commit under review and state that it is docs-only.
2. Rewrite the file list so it only includes the docs files changed in this commit.
3. Add a concrete scope-completed summary that explains the docs-only handoff alignment.
4. Preserve the roadmap and vision mapping for the earlier retrieval implementation without claiming it landed in this commit.
5. Document the `section:` compatibility boundary as an intentional MVP limitation until fallback support is restored.

### Files changed
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

### Compatibility note
- Breaking compatibility note: `section:` scopes are intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

### Guardrails
- Keep the handoff tied to the actual commit under review and its docs-only file set.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval tooling scope or cross-lane `section:` targeting.
- Ownership note: this fix changes only lane-owned docs artifacts and does not promote any shared or non-owned source files.
