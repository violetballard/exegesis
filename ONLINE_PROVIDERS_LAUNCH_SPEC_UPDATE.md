# Spec Update: Online Providers Available at Launch (No Online-Only SKU)

## Goal

- Online providers (OpenAI-compatible cloud and Anthropic Claude) are supported from launch.
- There is no online-only low-memory SKU at launch.
- Studio remains local-first with a 32GB minimum for confidential/local-inference workflows.
- Online providers are available only through explicit per-project profile switch.

## A) Profile Modes and Overrides (engine authoritative)

Engine profile modes:
- `confidential` (default)
- `standard` (online-capable, but cloud still gated)

Online provider activation:
- explicit `online_overrides.enabled=true` required for non-local providers

Engine `PolicyGate` provider allowlist:
- `confidential` => `local_openai` only (must be localhost)
- `standard` => `local_openai` + `openai_cloud` + `anthropic` (subject to online override gating)

## B) Cloud Send Policy (engine authoritative)

Default for non-local runs:
- `cloud_send_policy=context_sets_only`

`allow_full_doc` behavior:
- never default
- requires explicit per-run flag: `cloud_full_doc_ok=true`
- must emit audit event: `cloud_full_doc_used`

## C) Routing (unchanged baseline)

- Role-based routing remains:
  - `terminal_chat=Magistral`
  - `editor=Mistral`
  - `planner_deep=Qwen`
  - `bulk_best=GPT-OSS`
- Standard-mode runs may apply role overrides via `online_overrides.roles` when `online_overrides.enabled=true` (for example, `planner_deep -> anthropic`).
- No user-facing model pickers required; Admin Console remains the advanced config surface.

## D) Profiles (local runtime tiers only)

- Profiles remain local runtime references (`ctx/kv/quant/modes`).
- Profiles do not gate online availability.
- Remove/avoid online-SKU terminology from launch docs/config language.

## E) Launch Positioning

- Minimum supported Studio spec for confidential/local-inference workflows remains `32GB`.
- Online-provider use is an explicit override state, not a separate SKU.
- Standard-profile projects may run on lower-memory machines when local inference is not required.
- Future option to introduce an online-only lower-cost SKU is explicitly out of launch scope.

## F) UI Requirements (Studio/Web Console)

- UI must show provider used per run.
- UI must display a persistent banner when online overrides are enabled.

## Acceptance Criteria

1. Engine blocks any non-local provider in confidential mode.
2. Standard profile + online overrides can route selected roles to `openai_cloud` or `anthropic`.
3. Default `cloud_send_policy=context_sets_only` is enforced for all non-local runs.
4. No online-only SKU exists in launch config, pricing, or codepaths.
5. UI shows provider used per run and persistent online-enabled project banner.
