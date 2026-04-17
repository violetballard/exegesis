# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Exact canonical demo-path steps advanced: `open project/document`,
  `retrieve relevant material`, and `preview and apply or reject a patch`.
- Primary branch-tip step: `open project/document`. The active runtime change
  keeps `document-open` and `open-document` normalized onto the canonical
  `bootstrap` parser entrypoint instead of creating a divergent document-open
  surface.
- Supporting contract guard: parser entrypoints and catalog ordering can no
  longer drift silently away from the operator contract for those steps;
  `command_cli_contract()` now fails fast when the parser and catalog diverge.
- Scope boundary: this slice stays in CLI compatibility, command-catalog
  validation, alias normalization, and focused regression coverage. It does not
  add new commands, new flags, handler logic, or a wider MVP loop.

## Scope Tightening

- Roadmap impact: preserve deterministic CLI compatibility for the current
  engine-first MVP command path across bootstrap, retrieval, and diff preview,
  including document-open compatibility aliases routing through bootstrap.
- Vision impact: keep the canonical engine contract stable by making the active
  command surface explicit, keeping document-open aliases on the bootstrap
  route, and failing fast when parser/catalog ordering drifts instead of
  silently changing the operator-facing demo path.
