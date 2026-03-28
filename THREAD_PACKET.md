## Thread Handoff Packet

- Branch name: `codex/feat-context-storage`
- Reviewed commit(s):
  - `47cda4df831ac41867a8792f40d720e0cb109514`
- Final head SHA:
  - `f36909cca41b0717ef1b2eb0591254703c389d03`

## Scope completed

The fix stayed within the owned context/storage paths: `src/qual/context/**` and `src/qual/storage/**` were updated so recovery cleanup keeps the existing `updated_at` while stripping `recovered_from` provenance. The handoff packet and lane metadata were reissued to remove the stray `scripts/scope-check.sh` reference from the reviewed file list, leaving only the approved shared test exception in `tests/unit/test_context_storage_recovery.py`. No `engine/src/exegesis_engine/state/**` or `engine/src/exegesis_engine/storage/**` changes were needed for this recovery pass.

## Files changed

- `src/qual/context/set_store.py`
- `src/qual/context/store.py`
- `src/qual/storage/vault.py`
- `tests/unit/test_context_storage_recovery.py`

## Tasks completed

1. Reused the existing cleanup timestamp in `ContextBasketStore` recovery so canonical cleanup rewrites keep the prior `updated_at` value.
2. Reused the existing cleanup timestamp in `ContextSetStore` recovery so canonical cleanup rewrites keep the prior `updated_at` value.
3. Reused the existing cleanup timestamp in `VaultService` recovery so canonical cleanup rewrites keep the prior `updated_at` value.
4. Added regression coverage for preserved `updated_at` behavior in basket, context set, and vault recovery paths.
5. Reissued the handoff packet, lane metadata, and routed packet copy so the reviewed file list no longer includes `scripts/scope-check.sh` and stays synchronized under the approved handoff-artifact exception.
6. Updated the final head bookkeeping to the current branch tip.

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `MEDIUM`
- Blockers: none

## Roadmap item(s) affected

- Milestone 1 - Bootstrap Flow Stabilization: context basket and vault persistence hardening.

## Vision capability affected

- Capability 1 - Local-first state and identity.

## Routing/provider impact note

- None

## Approved exception note

- Approved shared/integrator-locked file exception for `THREAD_PACKET.md`, `.codex/lane_meta/feat-context-storage.json`, and `.codex/packets/lanes/feat-context-storage/inbox/feature/F__codex-feat-context-storage__6ca617ccf17f5da8f8270345fd41d48b68909ab7__20260328T204224Z.md`; these handoff artifacts must be updated together so the packet and lane bookkeeping match. Approved lane regression-test exception for `tests/unit/test_context_storage_recovery.py`; provenance documented in `.codex/packets/lanes/feat-context-storage/inbox/feature/F__codex-feat-context-storage__7b756291349fb12b27d07cf355a9b1b863759aa2__20260328T173918Z.md`.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits are limited to `src/qual/context/**` and `src/qual/storage/**`. The non-owned handoff artifacts listed above are updated only to record the review handoff and lane bookkeeping, and `tests/unit/test_context_storage_recovery.py` is covered by the lane-approved regression-test exception referenced above.
