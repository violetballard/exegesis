# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Reviewer Fix Alignment

- The current branch tip is a metadata-only fixer refresh commit on top of
  later lane work already present on `codex/feat-commands`.
- Review the command-catalog implementation at
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- For this re-review, use the reviewer packet as the scope source of truth and
  keep the reviewed implementation pinned to that command-catalog slice unless
  a new feature packet is explicitly generated.
- This refresh corrects handoff metadata only and does not expand the
  requested re-review scope beyond that command-catalog slice.
- This re-review refresh is specifically for the reviewer-requested packet fix:
  state explicitly which canonical demo-path step the work makes more real,
  while keeping the implementation review pinned to the same command-catalog
  slice.
- Reviewer-required fixes are satisfied on this branch by:
  - implementation-level parser-surface validation in
    `src/qual/commands/catalog.py`
  - regression coverage in `tests/unit/test_commands_catalog.py` for
    parser-surface drift that preserves canonical order
  - explicit canonical demo-path step mapping in `THREAD_PACKET.md`
- Feature-fixer validation on `2026-04-17`: the required local gates were
  rerun and passed on this metadata-refresh branch tip:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- This metadata-only fixer refresh does not change implementation files; it
  only refreshes the handoff contract for re-review after confirming the code
  and tests already satisfy the reviewer-required fixes on this branch.
- Concrete blocker-removal statement for AGENTS alignment: while the CLI is
  still the active operator surface, the engine-first MVP loop cannot stay
  dependable if the `bootstrap`, `context-basket`, and `diff-preview`
  entrypoints can drift away from the declared catalog without failing fast.
  This handoff now states that blocker explicitly.
- Canonical demo-path step impact: this slice makes the CLI `open
  project/document`, `retrieve relevant material`, and `preview and apply or
  reject a patch` steps, and the ongoing CLI operator path that must remain
  executable while Textual stays disabled, more reliable by keeping the
  `bootstrap`, `context-basket`, and `diff-preview` entrypoints aligned with
  the canonical command catalog and rejecting parser/catalog drift before it
  can silently change the operator-facing contract.
