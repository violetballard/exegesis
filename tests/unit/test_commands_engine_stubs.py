from __future__ import annotations

import unittest

from src.qual.commands.engine_stubs import (
    ENGINE_LOOP_NOT_WIRED,
    REVISE_BLOCKER_STEP,
    SESSION_RESUME_BLOCKER_STEP,
    SESSION_SAVE_BLOCKER_STEP,
    ReviseInput,
    ReviseResult,
    SessionResumeInput,
    SessionResumeResult,
    SessionSaveInput,
    SessionSaveResult,
    run_revise,
    run_session_resume,
    run_session_save,
)


class ReviseStubTests(unittest.TestCase):
    def test_run_revise_returns_not_ready(self) -> None:
        result = run_revise(ReviseInput(document_id="doc-1", basket_item_ids=()))
        self.assertIsInstance(result, ReviseResult)
        self.assertFalse(result.ready)

    def test_run_revise_echoes_document_id(self) -> None:
        result = run_revise(ReviseInput(document_id="doc-42", basket_item_ids=("item-1",)))
        self.assertEqual(result.document_id, "doc-42")

    def test_run_revise_blocker_step_is_canonical(self) -> None:
        result = run_revise(ReviseInput(document_id="doc-1", basket_item_ids=()))
        self.assertEqual(result.blocker_step, REVISE_BLOCKER_STEP)
        self.assertEqual(result.blocker_step, "produce-plan-or-revision")

    def test_run_revise_blocker_reason_signals_engine_gap(self) -> None:
        result = run_revise(ReviseInput(document_id="doc-1", basket_item_ids=()))
        self.assertEqual(result.blocker_reason, ENGINE_LOOP_NOT_WIRED)
        self.assertIn("feat-engine-runs", result.blocker_reason)

    def test_run_revise_is_deterministic(self) -> None:
        payload = ReviseInput(document_id="doc-1", basket_item_ids=("a", "b"))
        self.assertEqual(run_revise(payload), run_revise(payload))

    def test_run_revise_accepts_empty_basket(self) -> None:
        result = run_revise(ReviseInput(document_id="doc-1", basket_item_ids=()))
        self.assertFalse(result.ready)

    def test_run_revise_accepts_non_empty_basket(self) -> None:
        result = run_revise(ReviseInput(document_id="doc-1", basket_item_ids=("ctx-a", "ctx-b")))
        self.assertFalse(result.ready)


class SessionSaveStubTests(unittest.TestCase):
    def test_run_session_save_returns_not_ready(self) -> None:
        result = run_session_save(SessionSaveInput(document_id="doc-1", session_id="sess-1"))
        self.assertIsInstance(result, SessionSaveResult)
        self.assertFalse(result.ready)

    def test_run_session_save_echoes_document_and_session_ids(self) -> None:
        result = run_session_save(SessionSaveInput(document_id="doc-7", session_id="sess-99"))
        self.assertEqual(result.document_id, "doc-7")
        self.assertEqual(result.session_id, "sess-99")

    def test_run_session_save_blocker_step_is_canonical(self) -> None:
        result = run_session_save(SessionSaveInput(document_id="doc-1", session_id="sess-1"))
        self.assertEqual(result.blocker_step, SESSION_SAVE_BLOCKER_STEP)
        self.assertEqual(result.blocker_step, "persist-updated-document-session-state")

    def test_run_session_save_blocker_reason_signals_engine_gap(self) -> None:
        result = run_session_save(SessionSaveInput(document_id="doc-1", session_id="sess-1"))
        self.assertEqual(result.blocker_reason, ENGINE_LOOP_NOT_WIRED)
        self.assertIn("feat-engine-runs", result.blocker_reason)

    def test_run_session_save_is_deterministic(self) -> None:
        payload = SessionSaveInput(document_id="doc-1", session_id="sess-1")
        self.assertEqual(run_session_save(payload), run_session_save(payload))


class SessionResumeStubTests(unittest.TestCase):
    def test_run_session_resume_returns_not_ready(self) -> None:
        result = run_session_resume(SessionResumeInput(session_id="sess-1"))
        self.assertIsInstance(result, SessionResumeResult)
        self.assertFalse(result.ready)

    def test_run_session_resume_echoes_session_id(self) -> None:
        result = run_session_resume(SessionResumeInput(session_id="sess-42"))
        self.assertEqual(result.session_id, "sess-42")

    def test_run_session_resume_blocker_step_is_canonical(self) -> None:
        result = run_session_resume(SessionResumeInput(session_id="sess-1"))
        self.assertEqual(result.blocker_step, SESSION_RESUME_BLOCKER_STEP)
        self.assertEqual(result.blocker_step, "continue-without-losing-context")

    def test_run_session_resume_blocker_reason_signals_engine_gap(self) -> None:
        result = run_session_resume(SessionResumeInput(session_id="sess-1"))
        self.assertEqual(result.blocker_reason, ENGINE_LOOP_NOT_WIRED)
        self.assertIn("feat-engine-runs", result.blocker_reason)

    def test_run_session_resume_is_deterministic(self) -> None:
        payload = SessionResumeInput(session_id="sess-1")
        self.assertEqual(run_session_resume(payload), run_session_resume(payload))


class EngineStubsContractTests(unittest.TestCase):
    """Pins the stable contract shape so feat-engine-runs knows what to replace."""

    def test_blocker_step_constants_match_canonical_demo_path_gap_reasons(self) -> None:
        # These must stay aligned with CANONICAL_DEMO_PATH_GAP_REASONS in catalog.py.
        self.assertEqual(REVISE_BLOCKER_STEP, "produce-plan-or-revision")
        self.assertEqual(SESSION_SAVE_BLOCKER_STEP, "persist-updated-document-session-state")
        self.assertEqual(SESSION_RESUME_BLOCKER_STEP, "continue-without-losing-context")

    def test_engine_loop_not_wired_constant_references_downstream_lane(self) -> None:
        self.assertIn("feat-engine-runs", ENGINE_LOOP_NOT_WIRED)

    def test_all_stubs_share_same_blocker_reason(self) -> None:
        revise = run_revise(ReviseInput(document_id="d", basket_item_ids=()))
        save = run_session_save(SessionSaveInput(document_id="d", session_id="s"))
        resume = run_session_resume(SessionResumeInput(session_id="s"))
        self.assertEqual(revise.blocker_reason, save.blocker_reason)
        self.assertEqual(save.blocker_reason, resume.blocker_reason)

    def test_all_stubs_return_ready_false(self) -> None:
        revise = run_revise(ReviseInput(document_id="d", basket_item_ids=()))
        save = run_session_save(SessionSaveInput(document_id="d", session_id="s"))
        resume = run_session_resume(SessionResumeInput(session_id="s"))
        self.assertFalse(revise.ready)
        self.assertFalse(save.ready)
        self.assertFalse(resume.ready)


if __name__ == "__main__":
    unittest.main()
