# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before this handoff refresh commit: `81e954da3f89e7b47b3adb3560d476fef87fdcba`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the retrieval lane FTS-first for the MVP by removing the non-canonical `fetch_excerpt` PageIndex fallback and preserving deterministic excerpt provenance on the SQLite FTS path used before basket promotion.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This narrowed slice makes `retrieve relevant material` more real by removing the `fetch_excerpt` PageIndex fallback, which keeps excerpt provenance deterministic on the FTS-first retrieval path used before basket promotion.
- AGENTS-required canonical step mapping: The concrete Milestone 3 step advanced by this handoff is `retrieve relevant material`, specifically through the FTS-only `fetch_excerpt` behavior in the reviewed slice above.

## Scope Completed

- Removed the non-canonical PageIndex fallback from `fetch_excerpt(...)` so excerpt lookup now resolves through the authoritative SQLite FTS path only.
- Preserved deterministic excerpt provenance on the FTS-first retrieval flow used before basket promotion by failing closed when callers present PageIndex-only excerpt IDs.
- Kept the reviewed scope narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; this packet does not claim the full retrieval MVP is complete.
- Re-ran the required gate suite on the current packet-refresh branch head without changing the reviewed implementation head.
