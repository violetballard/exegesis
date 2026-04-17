# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Reviewer Fix Alignment

- This refresh is metadata-only for the active `codex/feat-commands` branch state.
- The reviewed implementation slice remains pinned to
  `05c0b20ff5e83e02d3ebadabbe39815d0afc0520` until a broader feature packet is generated.
- Revalidated on `2026-04-17` with passing `make scope-check`,
  `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`,
  `./typecheck-test.sh`, and `make ci`.
- Final fixer rerun on `2026-04-17` also repeated
  `python -m unittest tests.unit.test_commands_catalog -q` and confirmed the
  focused parser-surface drift coverage is still green on the handoff commit path.
- This pointer refresh records the final same-day feature-fixer verification
  for the reviewed branch-tip implementation so the handoff packet carries
  fresh gate evidence for the reviewer-required demo-path mapping fix.
- This latest metadata-only refresh also serves as the new branch-tip commit
  for the fixer rerun, without changing the reviewed implementation scope.
- `THREAD_PACKET.md` now also states the stricter parser-surface guarantee:
  canonical CLI entrypoints cannot be dropped, substituted, reordered, or
  expanded unexpectedly without failing the contract.
- Review the command-catalog implementation in `src/qual/commands/catalog.py` together with the focused shared-test coverage in `tests/unit/test_commands_catalog.py`.
- This regenerated handoff supersedes the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  implementation pin for re-review; review the current branch tip while
  keeping scope limited to the same command-catalog slice plus the approved
  shared test.
- `THREAD_PACKET.md` now names the canonical demo-path step advanced as
  `open project/document`, limits the vision mapping to the demonstrated CLI
  contract scope, and records the concrete shared-file approval basis required
  by the reviewer.
- `THREAD_PACKET.md` now also ties each completed task directly to the
  `open project/document` step and restates that the slice hardens existing
  command entrypoints only, without broadening the command surface.
- `THREAD_PACKET.md` now frames the contract-hardening rationale around the
  single `bootstrap` entrypoint for `open project/document`, rather than the
  broader CLI loop, so the re-review packet stays scope-tight.
- This final fixer refresh also records the approval provenance explicitly:
  the user-supplied `2026-04-17` reviewer packet for this run is the source of
  truth for the approved shared-test exception on
  `tests/unit/test_commands_catalog.py`.
