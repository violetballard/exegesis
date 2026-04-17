# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Exact canonical demo-path steps advanced: `open project/document`,
  `retrieve relevant material`, `preview and apply or reject a patch`, and
  `save and continue`.
- Why these steps: the reviewed command-surface work now keeps parser tokens,
  parser-native demo invocations, shim aliases, smoke/demo invocation plans,
  and terminal/export compatibility routing aligned with the canonical catalog
  instead of relying on implicit behavior.
- Scope boundary: this slice stays in CLI compatibility and command-surface
  routing. It does not add new engine business logic, add new command behavior,
  or widen the MVP loop.

## Scope Tightening

- Roadmap impact: preserve deterministic CLI compatibility for the current
  engine-first MVP command path across bootstrap, retrieval, diff preview, and
  terminal/export routing.
- Vision impact: keep the canonical engine contract stable by making the active
  command surface explicit, parser-ready, and fail-fast when parser/catalog
  routing drifts instead of silently changing the operator-facing demo path.
