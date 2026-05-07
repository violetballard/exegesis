"""Stable command compatibility surface for the CLI-first MVP loop."""

from src.qual.commands.catalog import *  # noqa: F401,F403
from src.qual.commands.canonical import *  # noqa: F401,F403
from src.qual.commands.diff_preview import (
    DiffPreviewInput,
    DiffPreviewResult,
    PatchReviewActionRoute,
    PatchReviewActionRouteValidation,
    PatchReviewCommandStatus,
    PatchReviewCommandStatusPayload,
    PatchReviewCommandContract,
    PatchReviewCommandSmokeContract,
    PatchReviewDecision,
    build_patch_review_command_contract,
    build_patch_review_command_smoke_contract,
    build_patch_review_action_route_lookup,
    build_patch_review_action_routes,
    build_diff_preview_result,
    build_patch_review_command_status_payload,
    build_patch_review_command_status,
    build_patch_review_decision,
    run_patch_review_action_route_lookup_json,
    run_patch_review_action_routes,
    run_patch_review_action_routes_json,
    run_patch_review_command_status,
    run_patch_review_command_status_json,
    run_patch_review_command_contract,
    run_patch_review_command_contract_json,
    run_patch_review_command_smoke_contract,
    run_patch_review_command_smoke_contract_json,
    run_patch_review_decision,
    run_patch_review_action_route_validation,
    run_patch_review_action_route_validation_json,
    run_diff_preview,
    validate_patch_review_action_routes,
    validate_patch_review_command_contract,
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
