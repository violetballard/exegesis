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
CONTEXT_STORAGE_NOT_WIRED = "context storage not yet wired: feat-context-storage must close this gap"
RETRIEVAL_NOT_WIRED = "FTS retrieval not yet wired: feat-retrieval-fts must close this gap"

REVISE_BLOCKER_STEP = "produce-plan-or-revision"
RETRIEVE_BLOCKER_STEP = "retrieve-relevant-material"
SESSION_SAVE_BLOCKER_STEP = "persist-updated-document-session-state"
SESSION_RESUME_BLOCKER_STEP = "continue-without-losing-context"
OPEN_PROJECT_BLOCKER_STEP = "open-project-document"
BASKET_ACTION_BLOCKER_STEP = "promote-or-gather-context-into-basket"
EXPORT_HANDOFF_BLOCKER_STEP = "export-handoff"


@dataclass(frozen=True)
class RetrieveInput:
    query: str

    def __post_init__(self) -> None:
        if not isinstance(self.query, str):
            raise TypeError("query must be a string")
        if not self.query.strip():
            raise ValueError("query cannot be empty or whitespace only")


@dataclass(frozen=True)
class RetrieveResult:
    ready: bool
    query: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.query, str):
            raise TypeError("query must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.query.strip():
            raise ValueError("query cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



def run_retrieve(payload: RetrieveInput) -> RetrieveResult:
    """Run an FTS retrieval query (stub)."""
    return RetrieveResult(
        ready=False,
        query=payload.query,
        blocker_step=RETRIEVE_BLOCKER_STEP,
        blocker_reason=RETRIEVAL_NOT_WIRED,
    )


@dataclass(frozen=True)
class ReviseInput:
    document_id: str
    basket_item_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not isinstance(self.basket_item_ids, tuple):
            raise TypeError("basket_item_ids must be a tuple")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        for item_id in self.basket_item_ids:
            if not isinstance(item_id, str):
                raise TypeError("basket_item_id must be a string")
            if not item_id.strip():
                raise ValueError("basket_item_id cannot be empty or whitespace only")


@dataclass(frozen=True)
class ReviseResult:
    ready: bool
    document_id: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



@dataclass(frozen=True)
class SessionSaveInput:
    document_id: str
    session_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not isinstance(self.session_id, str):
            raise TypeError("session_id must be a string")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty or whitespace only")


@dataclass(frozen=True)
class SessionSaveResult:
    ready: bool
    document_id: str
    session_id: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not isinstance(self.session_id, str):
            raise TypeError("session_id must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



@dataclass(frozen=True)
class SessionResumeInput:
    session_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, str):
            raise TypeError("session_id must be a string")
        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty or whitespace only")


@dataclass(frozen=True)
class SessionResumeResult:
    ready: bool
    session_id: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.session_id, str):
            raise TypeError("session_id must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



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


@dataclass(frozen=True)
class OpenProjectInput:
    project_id: str
    document_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.project_id, str):
            raise TypeError("project_id must be a string")
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not self.project_id.strip():
            raise ValueError("project_id cannot be empty or whitespace only")


@dataclass(frozen=True)
class OpenProjectResult:
    ready: bool
    project_id: str
    document_id: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.project_id, str):
            raise TypeError("project_id must be a string")
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.project_id.strip():
            raise ValueError("project_id cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



@dataclass(frozen=True)
class BasketActionInput:
    action: str
    item_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.action, str):
            raise TypeError("action must be a string")
        if not isinstance(self.item_id, str):
            raise TypeError("item_id must be a string")
        if not self.action.strip():
            raise ValueError("action cannot be empty or whitespace only")


@dataclass(frozen=True)
class BasketActionResult:
    ready: bool
    action: str
    item_id: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.action, str):
            raise TypeError("action must be a string")
        if not isinstance(self.item_id, str):
            raise TypeError("item_id must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.action.strip():
            raise ValueError("action cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



@dataclass(frozen=True)
class ExportHandoffInput:
    document_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")


@dataclass(frozen=True)
class ExportHandoffResult:
    ready: bool
    document_id: str
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.document_id, str):
            raise TypeError("document_id must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")



def run_open_project(payload: OpenProjectInput) -> OpenProjectResult:
    """Open a project and optional document (stub)."""
    return OpenProjectResult(
        ready=False,
        project_id=payload.project_id,
        document_id=payload.document_id,
        blocker_step=OPEN_PROJECT_BLOCKER_STEP,
        blocker_reason=CONTEXT_STORAGE_NOT_WIRED,
    )


def run_basket_action(payload: BasketActionInput) -> BasketActionResult:
    """Execute a context-basket action (list or add) (stub)."""
    return BasketActionResult(
        ready=False,
        action=payload.action,
        item_id=payload.item_id,
        blocker_step=BASKET_ACTION_BLOCKER_STEP,
        blocker_reason=CONTEXT_STORAGE_NOT_WIRED,
    )


def run_export_handoff(payload: ExportHandoffInput) -> ExportHandoffResult:
    """Run the terminal export handoff for a document (stub)."""
    return ExportHandoffResult(
        ready=False,
        document_id=payload.document_id,
        blocker_step=EXPORT_HANDOFF_BLOCKER_STEP,
        blocker_reason=ENGINE_LOOP_NOT_WIRED,
    )


@dataclass(frozen=True)
class NotebookActionInput:
    action: str
    target: str
    target_extra: str = ""
    target_tokens: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action, str):
            raise TypeError("action must be a string")
        if not isinstance(self.target, str):
            raise TypeError("target must be a string")
        if not isinstance(self.target_extra, str):
            raise TypeError("target_extra must be a string")
        if self.target_tokens is not None:
            if not isinstance(self.target_tokens, int):
                raise TypeError("target_tokens must be an integer or None")
            if self.target_tokens <= 0:
                raise ValueError("target_tokens must be a positive integer")
        if not self.action.strip():
            raise ValueError("action cannot be empty or whitespace only")
        if not self.target.strip():
            raise ValueError("target cannot be empty or whitespace only")


@dataclass(frozen=True)
class NotebookActionResult:
    ready: bool
    action: str
    target: str
    target_extra: str
    target_tokens: int | None
    blocker_step: str
    blocker_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.action, str):
            raise TypeError("action must be a string")
        if not isinstance(self.target, str):
            raise TypeError("target must be a string")
        if not isinstance(self.target_extra, str):
            raise TypeError("target_extra must be a string")
        if self.target_tokens is not None:
            if not isinstance(self.target_tokens, int):
                raise TypeError("target_tokens must be an integer or None")
            if self.target_tokens <= 0:
                raise ValueError("target_tokens must be a positive integer")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not self.action.strip():
            raise ValueError("action cannot be empty or whitespace only")
        if not self.target.strip():
            raise ValueError("target cannot be empty or whitespace only")
        if not self.blocker_step.strip():
            raise ValueError("blocker_step cannot be empty or whitespace only")


def run_notebook(payload: NotebookActionInput) -> NotebookActionResult:
    """Execute a notebook context command (stub)."""
    if payload.action in {"budget", "compact", "compactions", "expand-compaction"}:
        return NotebookActionResult(
            ready=False,
            action=payload.action,
            target=payload.target,
            target_extra=payload.target_extra,
            target_tokens=payload.target_tokens,
            blocker_step=REVISE_BLOCKER_STEP,
            blocker_reason=ENGINE_LOOP_NOT_WIRED,
        )
    else:  # restore-raw, pin, unpin
        return NotebookActionResult(
            ready=False,
            action=payload.action,
            target=payload.target,
            target_extra=payload.target_extra,
            target_tokens=payload.target_tokens,
            blocker_step=BASKET_ACTION_BLOCKER_STEP,
            blocker_reason=CONTEXT_STORAGE_NOT_WIRED,
        )
