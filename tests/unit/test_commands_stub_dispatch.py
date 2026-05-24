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
)
from src.qual.commands.stub_dispatch import (
    PARTIAL_COMMAND_TOKENS,
    REVISE_COMMAND,
    SESSION_RESUME_COMMAND,
    SESSION_SAVE_COMMAND,
    ArgvParseError,
    UnknownCommandError,
    dispatch_partial_command,
    dispatch_revise,
    dispatch_session_resume,
    dispatch_session_save,
    parse_revise_argv,
    parse_session_resume_argv,
    parse_session_save_argv,
)


class ParseReviseArgvTests(unittest.TestCase):
    def test_valid_argv_with_no_basket_items(self) -> None:
        result = parse_revise_argv(("revise", "doc-1"))
        self.assertIsInstance(result, ReviseInput)
        assert isinstance(result, ReviseInput)
        self.assertEqual(result.document_id, "doc-1")
        self.assertEqual(result.basket_item_ids, ())

    def test_valid_argv_with_basket_items(self) -> None:
        result = parse_revise_argv(("revise", "doc-2", "item-a", "item-b"))
        self.assertIsInstance(result, ReviseInput)
        assert isinstance(result, ReviseInput)
        self.assertEqual(result.document_id, "doc-2")
        self.assertEqual(result.basket_item_ids, ("item-a", "item-b"))

    def test_missing_document_id_returns_error(self) -> None:
        result = parse_revise_argv(("revise",))
        self.assertIsInstance(result, ArgvParseError)
        assert isinstance(result, ArgvParseError)
        self.assertEqual(result.command, REVISE_COMMAND)
        self.assertIn("document_id", result.reason)

    def test_error_includes_usage(self) -> None:
        result = parse_revise_argv(("revise",))
        assert isinstance(result, ArgvParseError)
        self.assertIn("revise", result.usage)
        self.assertIn("document_id", result.usage)

    def test_empty_argv_returns_error(self) -> None:
        result = parse_revise_argv(())
        self.assertIsInstance(result, ArgvParseError)

    def test_parse_is_deterministic(self) -> None:
        argv = ("revise", "doc-x", "ctx-1")
        self.assertEqual(parse_revise_argv(argv), parse_revise_argv(argv))


class ParseSessionSaveArgvTests(unittest.TestCase):
    def test_valid_argv(self) -> None:
        result = parse_session_save_argv(("session-save", "doc-1", "sess-99"))
        self.assertIsInstance(result, SessionSaveInput)
        assert isinstance(result, SessionSaveInput)
        self.assertEqual(result.document_id, "doc-1")
        self.assertEqual(result.session_id, "sess-99")

    def test_missing_session_id_returns_error(self) -> None:
        result = parse_session_save_argv(("session-save", "doc-1"))
        self.assertIsInstance(result, ArgvParseError)
        assert isinstance(result, ArgvParseError)
        self.assertEqual(result.command, SESSION_SAVE_COMMAND)
        self.assertIn("session_id", result.reason)

    def test_missing_both_args_returns_error(self) -> None:
        result = parse_session_save_argv(("session-save",))
        self.assertIsInstance(result, ArgvParseError)

    def test_error_includes_usage(self) -> None:
        result = parse_session_save_argv(("session-save", "doc-1"))
        assert isinstance(result, ArgvParseError)
        self.assertIn("session-save", result.usage)
        self.assertIn("session_id", result.usage)

    def test_parse_is_deterministic(self) -> None:
        argv = ("session-save", "doc-x", "sess-x")
        self.assertEqual(parse_session_save_argv(argv), parse_session_save_argv(argv))


class ParseSessionResumeArgvTests(unittest.TestCase):
    def test_valid_argv(self) -> None:
        result = parse_session_resume_argv(("session-resume", "sess-42"))
        self.assertIsInstance(result, SessionResumeInput)
        assert isinstance(result, SessionResumeInput)
        self.assertEqual(result.session_id, "sess-42")

    def test_missing_session_id_returns_error(self) -> None:
        result = parse_session_resume_argv(("session-resume",))
        self.assertIsInstance(result, ArgvParseError)
        assert isinstance(result, ArgvParseError)
        self.assertEqual(result.command, SESSION_RESUME_COMMAND)
        self.assertIn("session_id", result.reason)

    def test_error_includes_usage(self) -> None:
        result = parse_session_resume_argv(("session-resume",))
        assert isinstance(result, ArgvParseError)
        self.assertIn("session-resume", result.usage)

    def test_parse_is_deterministic(self) -> None:
        argv = ("session-resume", "sess-x")
        self.assertEqual(parse_session_resume_argv(argv), parse_session_resume_argv(argv))


class DispatchReviseTests(unittest.TestCase):
    def test_valid_argv_returns_revise_result(self) -> None:
        result = dispatch_revise(("revise", "doc-1"))
        self.assertIsInstance(result, ReviseResult)

    def test_result_is_not_ready(self) -> None:
        result = dispatch_revise(("revise", "doc-1"))
        assert isinstance(result, ReviseResult)
        self.assertFalse(result.ready)

    def test_result_echoes_document_id(self) -> None:
        result = dispatch_revise(("revise", "doc-abc"))
        assert isinstance(result, ReviseResult)
        self.assertEqual(result.document_id, "doc-abc")

    def test_result_has_canonical_blocker_step(self) -> None:
        result = dispatch_revise(("revise", "doc-1"))
        assert isinstance(result, ReviseResult)
        self.assertEqual(result.blocker_step, REVISE_BLOCKER_STEP)

    def test_invalid_argv_returns_parse_error(self) -> None:
        result = dispatch_revise(("revise",))
        self.assertIsInstance(result, ArgvParseError)

    def test_dispatch_is_deterministic(self) -> None:
        argv = ("revise", "doc-1", "item-1")
        self.assertEqual(dispatch_revise(argv), dispatch_revise(argv))

    def test_basket_items_flow_through(self) -> None:
        result = dispatch_revise(("revise", "doc-1", "ctx-a", "ctx-b"))
        assert isinstance(result, ReviseResult)
        self.assertFalse(result.ready)
        self.assertEqual(result.blocker_reason, ENGINE_LOOP_NOT_WIRED)


class DispatchSessionSaveTests(unittest.TestCase):
    def test_valid_argv_returns_session_save_result(self) -> None:
        result = dispatch_session_save(("session-save", "doc-1", "sess-1"))
        self.assertIsInstance(result, SessionSaveResult)

    def test_result_is_not_ready(self) -> None:
        result = dispatch_session_save(("session-save", "doc-1", "sess-1"))
        assert isinstance(result, SessionSaveResult)
        self.assertFalse(result.ready)

    def test_result_echoes_ids(self) -> None:
        result = dispatch_session_save(("session-save", "doc-7", "sess-99"))
        assert isinstance(result, SessionSaveResult)
        self.assertEqual(result.document_id, "doc-7")
        self.assertEqual(result.session_id, "sess-99")

    def test_result_has_canonical_blocker_step(self) -> None:
        result = dispatch_session_save(("session-save", "doc-1", "sess-1"))
        assert isinstance(result, SessionSaveResult)
        self.assertEqual(result.blocker_step, SESSION_SAVE_BLOCKER_STEP)

    def test_invalid_argv_returns_parse_error(self) -> None:
        result = dispatch_session_save(("session-save", "doc-1"))
        self.assertIsInstance(result, ArgvParseError)

    def test_dispatch_is_deterministic(self) -> None:
        argv = ("session-save", "doc-1", "sess-1")
        self.assertEqual(dispatch_session_save(argv), dispatch_session_save(argv))


class DispatchSessionResumeTests(unittest.TestCase):
    def test_valid_argv_returns_session_resume_result(self) -> None:
        result = dispatch_session_resume(("session-resume", "sess-1"))
        self.assertIsInstance(result, SessionResumeResult)

    def test_result_is_not_ready(self) -> None:
        result = dispatch_session_resume(("session-resume", "sess-1"))
        assert isinstance(result, SessionResumeResult)
        self.assertFalse(result.ready)

    def test_result_echoes_session_id(self) -> None:
        result = dispatch_session_resume(("session-resume", "sess-42"))
        assert isinstance(result, SessionResumeResult)
        self.assertEqual(result.session_id, "sess-42")

    def test_result_has_canonical_blocker_step(self) -> None:
        result = dispatch_session_resume(("session-resume", "sess-1"))
        assert isinstance(result, SessionResumeResult)
        self.assertEqual(result.blocker_step, SESSION_RESUME_BLOCKER_STEP)

    def test_invalid_argv_returns_parse_error(self) -> None:
        result = dispatch_session_resume(("session-resume",))
        self.assertIsInstance(result, ArgvParseError)

    def test_dispatch_is_deterministic(self) -> None:
        argv = ("session-resume", "sess-1")
        self.assertEqual(dispatch_session_resume(argv), dispatch_session_resume(argv))


class StubDispatchContractTests(unittest.TestCase):
    """Pins the dispatch contract shape so feat-engine-runs knows the calling convention."""

    def test_command_constants_match_catalog_entrypoints(self) -> None:
        self.assertEqual(REVISE_COMMAND, "revise")
        self.assertEqual(SESSION_SAVE_COMMAND, "session-save")
        self.assertEqual(SESSION_RESUME_COMMAND, "session-resume")

    def test_all_dispatchers_return_not_ready_on_valid_input(self) -> None:
        revise = dispatch_revise(("revise", "doc-1"))
        save = dispatch_session_save(("session-save", "doc-1", "sess-1"))
        resume = dispatch_session_resume(("session-resume", "sess-1"))
        self.assertIsInstance(revise, ReviseResult)
        self.assertIsInstance(save, SessionSaveResult)
        self.assertIsInstance(resume, SessionResumeResult)
        assert isinstance(revise, ReviseResult)
        assert isinstance(save, SessionSaveResult)
        assert isinstance(resume, SessionResumeResult)
        self.assertFalse(revise.ready)
        self.assertFalse(save.ready)
        self.assertFalse(resume.ready)

    def test_all_dispatchers_return_parse_error_on_missing_required_args(self) -> None:
        revise_err = dispatch_revise(("revise",))
        save_err = dispatch_session_save(("session-save", "doc-1"))
        resume_err = dispatch_session_resume(("session-resume",))
        self.assertIsInstance(revise_err, ArgvParseError)
        self.assertIsInstance(save_err, ArgvParseError)
        self.assertIsInstance(resume_err, ArgvParseError)

    def test_parse_errors_carry_command_name(self) -> None:
        revise_err = dispatch_revise(("revise",))
        save_err = dispatch_session_save(("session-save",))
        resume_err = dispatch_session_resume(("session-resume",))
        assert isinstance(revise_err, ArgvParseError)
        assert isinstance(save_err, ArgvParseError)
        assert isinstance(resume_err, ArgvParseError)
        self.assertEqual(revise_err.command, REVISE_COMMAND)
        self.assertEqual(save_err.command, SESSION_SAVE_COMMAND)
        self.assertEqual(resume_err.command, SESSION_RESUME_COMMAND)

    def test_blocker_reason_names_downstream_lane(self) -> None:
        result = dispatch_revise(("revise", "doc-1"))
        assert isinstance(result, ReviseResult)
        self.assertIn("feat-engine-runs", result.blocker_reason)


class DispatchPartialCommandTests(unittest.TestCase):
    """Pins the top-level router so feat-engine-runs has a single dispatch entry point."""

    def test_routes_revise_to_revise_result(self) -> None:
        result = dispatch_partial_command(("revise", "doc-1"))
        self.assertIsInstance(result, ReviseResult)
        assert isinstance(result, ReviseResult)
        self.assertFalse(result.ready)
        self.assertEqual(result.document_id, "doc-1")

    def test_routes_session_save_to_session_save_result(self) -> None:
        result = dispatch_partial_command(("session-save", "doc-1", "sess-1"))
        self.assertIsInstance(result, SessionSaveResult)
        assert isinstance(result, SessionSaveResult)
        self.assertFalse(result.ready)
        self.assertEqual(result.document_id, "doc-1")
        self.assertEqual(result.session_id, "sess-1")

    def test_routes_session_resume_to_session_resume_result(self) -> None:
        result = dispatch_partial_command(("session-resume", "sess-1"))
        self.assertIsInstance(result, SessionResumeResult)
        assert isinstance(result, SessionResumeResult)
        self.assertFalse(result.ready)
        self.assertEqual(result.session_id, "sess-1")

    def test_unknown_token_returns_unknown_command_error(self) -> None:
        result = dispatch_partial_command(("no-such-command", "arg"))
        self.assertIsInstance(result, UnknownCommandError)
        assert isinstance(result, UnknownCommandError)
        self.assertEqual(result.token, "no-such-command")
        self.assertEqual(result.known_tokens, PARTIAL_COMMAND_TOKENS)

    def test_empty_argv_returns_unknown_command_error(self) -> None:
        result = dispatch_partial_command(())
        self.assertIsInstance(result, UnknownCommandError)
        assert isinstance(result, UnknownCommandError)
        self.assertEqual(result.token, "")

    def test_parse_error_propagates_through_router(self) -> None:
        # Missing required args for revise should yield ArgvParseError, not UnknownCommandError.
        result = dispatch_partial_command(("revise",))
        self.assertIsInstance(result, ArgvParseError)

    def test_partial_command_tokens_pins_all_three_in_demo_path_order(self) -> None:
        self.assertEqual(
            PARTIAL_COMMAND_TOKENS,
            (REVISE_COMMAND, SESSION_SAVE_COMMAND, SESSION_RESUME_COMMAND),
        )

    def test_router_is_deterministic(self) -> None:
        r1 = dispatch_partial_command(("revise", "doc-1"))
        r2 = dispatch_partial_command(("revise", "doc-1"))
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main()
