"""Stable command compatibility surface for the CLI-first MVP loop."""

from __future__ import annotations

import json
from dataclasses import asdict

from src.qual.commands.catalog import *  # noqa: F401,F403
from src.qual.commands.canonical import *  # noqa: F401,F403
from src.qual.commands.canonical import (
    canonical_command_command_surface_payload,
    canonical_command_demo_loop_payload,
    canonical_command_demo_loop_smoke_payload,
    canonical_command_exact_action_route_payload,
    canonical_command_execution_plan_payload,
    canonical_command_handler_trust_gate_payload,
    canonical_command_persist_continue_payload,
    canonical_command_readiness_command_audit_payload,
    canonical_command_readiness_cli_smoke_lines,
    canonical_command_readiness_next_status_payload,
    canonical_command_readiness_snapshot_payload,
    canonical_command_retrieval_context_payload,
)
from src.qual.commands.diff_preview import (
    DiffPreviewInput,
    DiffPreviewResult,
    PatchReviewActionRoute,
    PatchReviewActionRouteValidation,
    PatchReviewActionResolution,
    PatchReviewCommandStatus,
    PatchReviewCommandStatusPayload,
    PatchReviewCommandContract,
    PatchReviewCommandSmokeContract,
    PatchReviewDecision,
    PatchReviewReadinessContract,
    build_patch_review_command_contract,
    build_patch_review_command_smoke_contract,
    build_patch_review_action_route_lookup,
    build_patch_review_action_routes,
    build_patch_review_action_compatibility_aliases,
    build_diff_preview_result,
    build_patch_review_readiness_contract,
    build_patch_review_command_status_payload,
    build_patch_review_command_status,
    build_patch_review_decision,
    run_patch_review_action_route_lookup_json,
    run_patch_review_action_routes,
    run_patch_review_action_routes_json,
    run_patch_review_action_resolution,
    run_patch_review_action_resolution_json,
    run_patch_review_command_status,
    run_patch_review_command_status_json,
    run_patch_review_command_contract,
    run_patch_review_command_contract_json,
    run_patch_review_command_smoke_contract,
    run_patch_review_command_smoke_contract_json,
    run_patch_review_decision,
    run_patch_review_readiness_contract,
    run_patch_review_readiness_contract_json,
    run_patch_review_action_route_validation,
    run_patch_review_action_route_validation_json,
    run_diff_preview,
    resolve_patch_review_action,
    validate_patch_review_action_routes,
    validate_patch_review_command_contract,
)

def build_mvp_demo_command_surface_payload() -> dict[str, object]:
    """Return the deterministic package-level contract for the MVP demo loop."""
    demo_loop = canonical_command_demo_loop_payload()
    smoke_contract = canonical_command_demo_loop_smoke_payload()
    patch_review_contract = build_patch_review_command_contract()
    return {
        "is_ready": demo_loop["is_ready"],
        "issues": demo_loop["issues"],
        "demo_loop": demo_loop,
        "execution_plan": canonical_command_execution_plan_payload(),
        "retrieval_context": canonical_command_retrieval_context_payload(),
        "patch_review": asdict(patch_review_contract),
        "patch_review_readiness_smoke": build_patch_review_readiness_smoke_payload(),
        "persist_continue": canonical_command_persist_continue_payload(),
        "demo_path_commands": build_mvp_demo_path_command_payload(demo_loop),
        "readiness_snapshot": canonical_command_readiness_snapshot_payload(()),
        "next_command": canonical_command_readiness_next_status_payload(),
        "smoke_contract": smoke_contract,
        "smoke_command_lines": canonical_command_readiness_cli_smoke_lines(),
    }


def run_mvp_demo_command_surface_json() -> str:
    """Return the package-level MVP demo command contract as stable JSON."""
    return json.dumps(
        build_mvp_demo_command_surface_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_path_command_payload(
    demo_loop: dict[str, object] | None = None,
) -> tuple[dict[str, object], ...]:
    """Return demo-path steps mapped to the commands reviewers can smoke-test."""
    loop = demo_loop or canonical_command_demo_loop_payload()
    steps = tuple(loop["demo_path_steps"])
    command_lines = tuple(loop["command_lines"])
    smoke_argvs = tuple(loop["smoke_argvs"])
    action_lookup = dict(loop["action_lookup_table"])
    entries: list[dict[str, object]] = []
    for step, command_line, smoke_argv in zip(
        steps,
        command_lines,
        smoke_argvs,
        strict=True,
    ):
        entries.append(
            {
                "demo_path_step": step,
                "command_line": command_line,
                "smoke_argv": smoke_argv,
                "engine_actions": action_lookup[step],
            }
        )
    return tuple(entries)


def run_mvp_demo_path_command_json() -> str:
    """Return demo-path command audit data as stable JSON."""
    return json.dumps(
        build_mvp_demo_path_command_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_patch_review_readiness_smoke_payload() -> dict[str, object]:
    """Return changed/no-change patch-review readiness payloads for smoke checks."""
    changed_payload = DiffPreviewInput(
        "draft text before review\n",
        "revised draft text\n",
    )
    no_change_payload = DiffPreviewInput(
        "unchanged draft text\n",
        "unchanged draft text\n",
    )
    changed = build_patch_review_readiness_contract(changed_payload)
    no_change = build_patch_review_readiness_contract(no_change_payload)
    return {
        "ready": changed.ready and no_change.ready,
        "changed": asdict(changed),
        "no_change": asdict(no_change),
    }


def run_patch_review_readiness_smoke_json() -> str:
    """Return deterministic patch-review readiness smoke data as stable JSON."""
    return json.dumps(
        build_patch_review_readiness_smoke_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_command_surface_audit_payload() -> dict[str, object]:
    """Return a deterministic audit bundle for command-surface handoff checks."""
    return {
        "surface": build_mvp_demo_command_surface_payload(),
        "command_surface": canonical_command_command_surface_payload(),
        "handler_trust_gate": canonical_command_handler_trust_gate_payload(),
        "command_readiness_audit": canonical_command_readiness_command_audit_payload(),
        "exact_action_routes": canonical_command_exact_action_route_payload(),
        "demo_path_commands": build_mvp_demo_path_command_payload(),
        "patch_review_readiness_smoke": build_patch_review_readiness_smoke_payload(),
    }


def run_mvp_demo_command_surface_audit_json() -> str:
    """Return the MVP demo command-surface audit bundle as stable JSON."""
    return json.dumps(
        build_mvp_demo_command_surface_audit_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


__all__ = tuple(name for name in globals() if not name.startswith("_"))
