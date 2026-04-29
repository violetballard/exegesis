# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands`.
- Review basis: `git diff main...codex/feat-commands`.
- Scope: deterministic MVP command contract for the current command catalog, parser surface, smoke command lines, and demo-path checkpoints.
- Branch-tip implementation scope: includes `894e6c128e4e2ece1406f4e95f5086b774955905` (`Add MVP demo command lookup contract`), which adds `CommandDemoPathLookupContract` and public demo-path lookup exports in `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` explicitly use the canonical steps `open document`, `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, `persist/save`, and `continue`; this slice does not claim direct `plan/revise` implementation.
- Final readiness: the command-catalog slice now makes `retrieve material` and `gather/promote context` more real for the CLI-first Milestone 3 loop, while locking adjacent patch-review, persistence, and continuation handoffs.
- Shared-file exception: `src/qual/cli.py` is included in the full branch-tip review target because the actual argparse parser consumes catalog-owned CLI tokens; the `20260429T131018Z` fixer slice did not newly edit integrator-locked files.
- Shared-test exception: `tests/unit/test_commands_catalog.py` remains in the reviewed diff as the approved focused command-catalog regression surface.
- Fixer prompt satisfied: `20260429T133117Z`; canonical packet details live in `THREAD_PACKET.md`.
