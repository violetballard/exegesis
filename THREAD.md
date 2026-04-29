# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands`; the immediately prior reviewed tip was `6f0c7ebd627e0ff1de2738672bb0af1a06b0e93d`.
- Review basis: `git diff main...codex/feat-commands`, with the reviewer-called-out post-`f8d860e` delta explicitly recorded in `THREAD_PACKET.md`.
- Scope: deterministic MVP command contract for the current command catalog, parser surface, smoke command lines, and demo-path checkpoints.
- Branch-tip implementation scope: includes `894e6c128e4e2ece1406f4e95f5086b774955905` (`Add MVP demo command lookup contract`), which adds `CommandDemoPathLookupContract` and public demo-path lookup exports in `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
- Branch-tip test/handoff scope: includes `04974e20df08b704f39a065e6082194f9024fd26` (`fix(commands): satisfy branch tip lookup review`), which changes `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`; it is not metadata-only.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` explicitly use the canonical steps `open document`, `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, `persist/save`, and `continue`; this slice does not claim direct `plan/revise` implementation.
- Final readiness: the command-catalog slice now makes `retrieve material` and `gather/promote context` more real for the CLI-first Milestone 3 loop, while locking adjacent patch-review, persistence, and continuation handoffs.
- Shared-file exception: `src/qual/cli.py` is included in the full branch-tip review target because the actual argparse parser consumes catalog-owned CLI tokens; this remains an earlier full-branch exception, not a current fixer edit.
- Shared-test exception: `tests/unit/test_commands_catalog.py` remains in the reviewed diff as the approved focused command-catalog regression surface.
- Current fixer slice: `20260429T143425Z`; edits lane-owned `src/qual/commands/catalog.py`, approved shared test coverage in `tests/unit/test_commands_catalog.py`, and handoff metadata only.
- Current fixer shared/integrator-locked edits: NO integrator-locked file edits; no `src/qual/cli.py` edit in this slice.
- Fixer prompt satisfied: `20260429T143425Z`; canonical packet details live in `THREAD_PACKET.md`.
