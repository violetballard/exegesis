from __future__ import annotations

from dataclasses import dataclass

# Thin command handler stubs for the three partial-command blockers in the
# Milestone 3 demo path: produce-plan-or-revision, persist-updated-document-
# session-state, and continue-without-losing-context.
#
# Each stub returns ready=False and a stable blocker_reason string that
# feat-engine-runs consumes to know which engine integration is still missing.
# When the engine loop is wired, only the function body changes — the input/
# output shapes are the stable command contract.

ENGINE_LOOP_NOT_WIRED = "engine loop not yet wired: feat-engine-runs must close this gap"

REVISE_BLOCKER_STEP = "produce-plan-or-revision"
SESSION_SAVE_BLOCKER_STEP = "persist-updated-document-session-state"
SESSION_RESUME_BLOCKER_STEP = "continue-without-losing-context"


@dataclass(frozen=True)
class ReviseInput:
    document_id: str
    basket_item_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviseResult:
    ready: bool
    document_id: str
    blocker_step: str
    blocker_reason: str = ""


@dataclass(frozen=True)
class SessionSaveInput:
    document_id: str
    session_id: str


@dataclass(frozen=True)
class SessionSaveResult:
    ready: bool
    document_id: str
    session_id: str
    blocker_step: str
    blocker_reason: str = ""


@dataclass(frozen=True)
class SessionResumeInput:
    session_id: str


@dataclass(frozen=True)
class SessionResumeResult:
    ready: bool
    session_id: str
    blocker_step: str
    blocker_reason: str = ""


def run_revise(payload: ReviseInput) -> ReviseResult:
    """Produce a plan or revision through the engine loop (stub)."""
    return ReviseResult(
        ready=False,
        document_id=payload.document_id,
        blocker_step=REVISE_BLOCKER_STEP,
        blocker_reason=ENGINE_LOOP_NOT_WIRED,
    )


def run_session_save(payload: SessionSaveInput) -> SessionSaveResult:
    """Persist the updated document and session state (stub)."""
    return SessionSaveResult(
        ready=False,
        document_id=payload.document_id,
        session_id=payload.session_id,
        blocker_step=SESSION_SAVE_BLOCKER_STEP,
        blocker_reason=ENGINE_LOOP_NOT_WIRED,
    )


def run_session_resume(payload: SessionResumeInput) -> SessionResumeResult:
    """Resume the workflow without losing context (stub)."""
    return SessionResumeResult(
        ready=False,
        session_id=payload.session_id,
        blocker_step=SESSION_RESUME_BLOCKER_STEP,
        blocker_reason=ENGINE_LOOP_NOT_WIRED,
    )
