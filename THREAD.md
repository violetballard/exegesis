# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands`; the immediately prior reviewed tip was `e19ff6362a4b6f9cae64810dca7414b1c526ed99`.
- Review basis: `git diff main...codex/feat-commands`, with the reviewer-called-out post-`f8d860e` delta explicitly recorded in `THREAD_PACKET.md`.
- Scope: deterministic MVP command contract for the current command catalog, parser surface, smoke command lines, and demo-path checkpoints.
- Branch-tip implementation scope: includes `894e6c128e4e2ece1406f4e95f5086b774955905` (`Add MVP demo command lookup contract`), which adds `CommandDemoPathLookupContract` and public demo-path lookup exports in `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
- Branch-tip test/handoff scope: includes `04974e20df08b704f39a065e6082194f9024fd26` (`fix(commands): satisfy branch tip lookup review`), which changes `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`; it is not metadata-only.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` explicitly use the canonical steps `open document`, `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, `persist/save`, and `continue`; this slice does not claim direct `plan/revise` implementation.
- Final readiness: the command-catalog slice now makes `retrieve material` and `gather/promote context` more real for the CLI-first Milestone 3 loop, while locking adjacent patch-review, persistence, and continuation handoffs.
- Shared-file exception: `src/qual/cli.py` is included in the full branch-tip review target because the actual argparse parser consumes catalog-owned CLI tokens; the `20260429T131018Z` fixer slice did not newly edit integrator-locked files.
- Shared-test exception: `tests/unit/test_commands_catalog.py` remains in the reviewed diff as the approved focused command-catalog regression surface.
- Fixer prompt satisfied: `20260429T134945Z`; canonical packet details live in `THREAD_PACKET.md`.
