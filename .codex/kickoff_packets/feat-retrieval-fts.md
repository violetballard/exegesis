# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`
- Scope goal: Canonicalize FTS excerpt payloads in `src/qual/retrieval/service.py` so retrieval-backed fetches return stable payloads for downstream consumers.

### Priority outcomes
1. Remove stale retrieval-implementation claims from the handoff artifacts.
2. Keep the reviewed commit description limited to the three metadata files actually changed.
3. Avoid implying any retrieval source-code, PageIndex, or routing changes in this promotion.

### Guardrails
- Keep the change limited to handoff and lane metadata artifacts.
- Preserve commit accuracy between the packet, lane metadata, and git history.
- Do not reference unreviewed retrieval source files.
