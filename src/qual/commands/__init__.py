"""Stable command compatibility surface for the CLI-first MVP loop."""

from src.qual.commands.catalog import *  # noqa: F401,F403
from src.qual.commands.canonical import *  # noqa: F401,F403
from src.qual.commands.diff_preview import (
    DiffPreviewInput,
    DiffPreviewResult,
    PatchReviewCommandStatus,
    PatchReviewCommandStatusPayload,
    PatchReviewDecision,
    build_diff_preview_result,
    build_patch_review_command_status_payload,
    build_patch_review_command_status,
    build_patch_review_decision,
    run_patch_review_command_status,
    run_patch_review_command_status_json,
    run_patch_review_decision,
    run_diff_preview,
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
