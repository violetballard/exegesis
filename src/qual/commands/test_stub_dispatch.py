from __future__ import annotations

import unittest

from src.qual.commands.engine_stubs import (
    ENGINE_LOOP_NOT_WIRED,
    REVISE_BLOCKER_STEP,
    SESSION_RESUME_BLOCKER_STEP,
    SESSION_SAVE_BLOCKER_STEP,
    ReviseResult,
    SessionResumeResult,
    SessionSaveResult,
)
from src.qual.commands.stub_dispatch import (
    ArgvParseError,
    REVISE_COMMAND,
    SESSION_RESUME_COMMAND,
    SESSION_SAVE_COMMAND,
    dispatch_revise,
    dispatch_session_resume,
    dispatch_session_save,
    parse_revise_argv,
    parse_session_resume_argv,
    parse_session_save_argv,
)


class TestParseReviseArgv(unittest.TestCase):
    def test_valid_argv_with_basket_items(self) -> None:
        result = parse_revise_argv(("revise", "doc-1", "item-a", "item-b"))
        assert not isinstance(result, ArgvParseError)
        assert result.document_id == "doc-1"
        assert result.basket_item_ids == ("item-a", "item-b")

    def test_valid_argv_without_basket_items(self) -> None:
        result = parse_revise_argv(("revise", "doc-1"))
        assert not isinstance(result, ArgvParseError)
        assert result.document_id == "doc-1"
        assert result.basket_item_ids == ()

    def test_missing_document_id_returns_parse_error(self) -> None:
        result = parse_revise_argv(("revise",))
        assert isinstance(result, ArgvParseError)
        assert result.command == REVISE_COMMAND
        assert "document_id" in result.reason

    def test_empty_argv_returns_parse_error(self) -> None:
        result = parse_revise_argv(())
        assert isinstance(result, ArgvParseError)
        assert result.command == REVISE_COMMAND


class TestParseSessionSaveArgv(unittest.TestCase):
    def test_valid_argv(self) -> None:
        result = parse_session_save_argv(("session-save", "doc-2", "sess-99"))
        assert not isinstance(result, ArgvParseError)
        assert result.document_id == "doc-2"
        assert result.session_id == "sess-99"

    def test_missing_session_id_returns_parse_error(self) -> None:
        result = parse_session_save_argv(("session-save", "doc-2"))
        assert isinstance(result, ArgvParseError)
        assert result.command == SESSION_SAVE_COMMAND

    def test_empty_argv_returns_parse_error(self) -> None:
        result = parse_session_save_argv(())
        assert isinstance(result, ArgvParseError)
        assert result.command == SESSION_SAVE_COMMAND


class TestParseSessionResumeArgv(unittest.TestCase):
    def test_valid_argv(self) -> None:
        result = parse_session_resume_argv(("session-resume", "sess-42"))
        assert not isinstance(result, ArgvParseError)
        assert result.session_id == "sess-42"

    def test_missing_session_id_returns_parse_error(self) -> None:
        result = parse_session_resume_argv(("session-resume",))
        assert isinstance(result, ArgvParseError)
        assert result.command == SESSION_RESUME_COMMAND

    def test_empty_argv_returns_parse_error(self) -> None:
        result = parse_session_resume_argv(())
        assert isinstance(result, ArgvParseError)
        assert result.command == SESSION_RESUME_COMMAND


class TestDispatchRevise(unittest.TestCase):
    def test_valid_dispatch_returns_stub_result_not_ready(self) -> None:
        result = dispatch_revise(("revise", "doc-1", "item-a"))
        assert isinstance(result, ReviseResult)
        assert result.ready is False
        assert result.document_id == "doc-1"
        assert result.blocker_step == REVISE_BLOCKER_STEP
        assert result.blocker_reason == ENGINE_LOOP_NOT_WIRED

    def test_invalid_dispatch_returns_parse_error(self) -> None:
        result = dispatch_revise(("revise",))
        assert isinstance(result, ArgvParseError)
        assert result.command == REVISE_COMMAND

    def test_stub_blocker_reason_names_feat_engine_runs(self) -> None:
        result = dispatch_revise(("revise", "doc-1"))
        assert isinstance(result, ReviseResult)
        assert "feat-engine-runs" in result.blocker_reason


class TestDispatchSessionSave(unittest.TestCase):
    def test_valid_dispatch_returns_stub_result_not_ready(self) -> None:
        result = dispatch_session_save(("session-save", "doc-2", "sess-99"))
        assert isinstance(result, SessionSaveResult)
        assert result.ready is False
        assert result.document_id == "doc-2"
        assert result.session_id == "sess-99"
        assert result.blocker_step == SESSION_SAVE_BLOCKER_STEP
        assert result.blocker_reason == ENGINE_LOOP_NOT_WIRED

    def test_invalid_dispatch_returns_parse_error(self) -> None:
        result = dispatch_session_save(("session-save", "doc-2"))
        assert isinstance(result, ArgvParseError)
        assert result.command == SESSION_SAVE_COMMAND

    def test_stub_blocker_reason_names_feat_engine_runs(self) -> None:
        result = dispatch_session_save(("session-save", "doc-2", "sess-99"))
        assert isinstance(result, SessionSaveResult)
        assert "feat-engine-runs" in result.blocker_reason


class TestDispatchSessionResume(unittest.TestCase):
    def test_valid_dispatch_returns_stub_result_not_ready(self) -> None:
        result = dispatch_session_resume(("session-resume", "sess-42"))
        assert isinstance(result, SessionResumeResult)
        assert result.ready is False
        assert result.session_id == "sess-42"
        assert result.blocker_step == SESSION_RESUME_BLOCKER_STEP
        assert result.blocker_reason == ENGINE_LOOP_NOT_WIRED

    def test_invalid_dispatch_returns_parse_error(self) -> None:
        result = dispatch_session_resume(("session-resume",))
        assert isinstance(result, ArgvParseError)
        assert result.command == SESSION_RESUME_COMMAND

    def test_stub_blocker_reason_names_feat_engine_runs(self) -> None:
        result = dispatch_session_resume(("session-resume", "sess-42"))
        assert isinstance(result, SessionResumeResult)
        assert "feat-engine-runs" in result.blocker_reason


if __name__ == "__main__":
    unittest.main()
