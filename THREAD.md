# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Exact canonical demo-path steps advanced: `open project/document`,
  `retrieve relevant material`, and `preview and apply or reject a patch`.
- Concrete blocker removed: parser entrypoints and catalog ordering can no
  longer drift silently away from the operator contract for those steps;
  `command_cli_contract()` now fails fast when the parser and catalog diverge.
- Why these steps: the reviewed command-catalog work keeps the existing parser
  surface aligned with canonical command names and order instead of relying on
  implicit ordering assumptions.
- Scope boundary: this slice stays in CLI compatibility and command-catalog
  validation. It does not add new commands, new flags, handler logic, or a
  wider MVP loop.

## Scope Tightening

- Roadmap impact: preserve deterministic CLI compatibility for the current
  engine-first MVP command path across bootstrap, retrieval, and diff preview.
- Vision impact: keep the canonical engine contract stable by making the active
  command surface explicit and fail-fast when parser/catalog ordering drifts
  instead of silently changing the operator-facing demo path.
