# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Reviewed commit(s):
  - `36893f06df85409c4595d64adb8af60455c086a6`
  - `dc8f79e4abeb30de51854fdd84d35b97993955b8`
  - `f0047257cf71b750a576de84c272c0f8c5875148`
- Metadata-only follow-up commit:
  - `34dfec2f59175850da3d33e8e50b3641f1256b49`

## Scope completed

The packet now records the reviewed implementation commit set separately from the metadata-only follow-up commit, so the audit trail does not imply the follow-up commit is the feature payload.

### Reviewed implementation files (reference only)
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/service.py`

### Handoff correction note
- The current correction stays within the handoff artifacts only.

### Priority outcomes
1. Keep the reviewed commit set explicit and auditable.
2. Keep the metadata-only follow-up commit separate from the feature payload.
3. Keep the handoff correction limited to the handoff artifacts.
4. Keep the reviewed implementation files listed separately for traceability.

### Tasks
1. Add an explicit reviewed commit-set field to the handoff packet.
2. Separate the metadata-only follow-up commit from the reviewed implementation bundle.
3. Rewrite the scope text so the handoff artifact is auditable without inferring context.
4. Keep the reviewed implementation files listed separately for traceability.

### Files changed
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

### Compatibility note
- Breaking compatibility note: `section:` scopes are intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

### Guardrails
- Keep the handoff tied to the retrieval implementation and its lane-owned file set.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply cross-lane `section:` targeting.
- Ownership note: this handoff stays within `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.

### Scope-check / ownership note
- No non-retrieval tooling edits are approved for this handoff.
- No out-of-lane tooling files are included in this resubmission.
