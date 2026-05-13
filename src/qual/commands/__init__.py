"""Stable command compatibility surface for the CLI-first MVP loop."""

from __future__ import annotations

import json
from dataclasses import asdict

from src.qual.commands.catalog import *  # noqa: F401,F403
from src.qual.commands.canonical import *  # noqa: F401,F403
from src.qual.commands.canonical import (
    canonical_command_demo_loop_payload,
    canonical_command_demo_loop_smoke_payload,
    canonical_command_execution_plan_payload,
    canonical_command_persist_continue_payload,
    canonical_command_readiness_cli_smoke_lines,
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
    return {
        "is_ready": demo_loop["is_ready"],
        "issues": demo_loop["issues"],
        "demo_loop": demo_loop,
        "execution_plan": canonical_command_execution_plan_payload(),
        "retrieval_context": canonical_command_retrieval_context_payload(),
        "patch_review": asdict(build_patch_review_command_contract()),
        "persist_continue": canonical_command_persist_continue_payload(),
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


__all__ = tuple(name for name in globals() if not name.startswith("_"))
