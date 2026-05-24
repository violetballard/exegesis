from __future__ import annotations

import unittest

import src.qual.commands as commands
from src.qual.commands.catalog import CANONICAL_DEMO_PATH_PARTIAL_COMMANDS
from src.qual.commands.engine_stubs import (
    REVISE_BLOCKER_STEP,
    SESSION_RESUME_BLOCKER_STEP,
    SESSION_SAVE_BLOCKER_STEP,
)
from src.qual.commands.stub_dispatch import PARTIAL_COMMAND_TOKENS


class CommandsPackageSurfaceTests(unittest.TestCase):
    """Pin that engine stub and dispatch contracts are importable from the package root.

    feat-engine-runs imports these symbols to wire the engine loop into the
    partial-command stubs. Keeping them accessible at the package level means
    feat-engine-runs never needs to know the internal module layout.
    """

    def test_engine_loop_not_wired_constant_is_exported(self) -> None:
        self.assertIsInstance(commands.ENGINE_LOOP_NOT_WIRED, str)
        self.assertIn("feat-engine-runs", commands.ENGINE_LOOP_NOT_WIRED)

    def test_blocker_step_constants_are_exported(self) -> None:
        self.assertEqual(commands.REVISE_BLOCKER_STEP, "produce-plan-or-revision")
        self.assertEqual(commands.SESSION_SAVE_BLOCKER_STEP, "persist-updated-document-session-state")
        self.assertEqual(commands.SESSION_RESUME_BLOCKER_STEP, "continue-without-losing-context")

    def test_command_name_constants_are_exported(self) -> None:
        self.assertEqual(commands.REVISE_COMMAND, "revise")
        self.assertEqual(commands.SESSION_SAVE_COMMAND, "session-save")
        self.assertEqual(commands.SESSION_RESUME_COMMAND, "session-resume")

    def test_input_types_are_exported(self) -> None:
        payload = commands.ReviseInput(document_id="doc-1", basket_item_ids=())
        self.assertEqual(payload.document_id, "doc-1")

        save_payload = commands.SessionSaveInput(document_id="doc-1", session_id="sess-1")
        self.assertEqual(save_payload.session_id, "sess-1")

        resume_payload = commands.SessionResumeInput(session_id="sess-2")
        self.assertEqual(resume_payload.session_id, "sess-2")

    def test_result_types_are_exported(self) -> None:
        self.assertTrue(hasattr(commands, "ReviseResult"))
        self.assertTrue(hasattr(commands, "SessionSaveResult"))
        self.assertTrue(hasattr(commands, "SessionResumeResult"))

    def test_dispatch_functions_are_exported(self) -> None:
        self.assertTrue(callable(commands.dispatch_revise))
        self.assertTrue(callable(commands.dispatch_session_save))
        self.assertTrue(callable(commands.dispatch_session_resume))

    def test_parse_functions_are_exported(self) -> None:
        self.assertTrue(callable(commands.parse_revise_argv))
        self.assertTrue(callable(commands.parse_session_save_argv))
        self.assertTrue(callable(commands.parse_session_resume_argv))

    def test_argv_parse_error_type_is_exported(self) -> None:
        err = commands.ArgvParseError(command="revise", reason="missing arg", usage="revise <doc_id>")
        self.assertEqual(err.command, "revise")

    def test_stub_runners_are_exported(self) -> None:
        self.assertTrue(callable(commands.run_revise))
        self.assertTrue(callable(commands.run_session_save))
        self.assertTrue(callable(commands.run_session_resume))

    def test_dispatch_revise_via_package_root_returns_not_ready(self) -> None:
        result = commands.dispatch_revise(("revise", "doc-42"))
        self.assertIsInstance(result, commands.ReviseResult)
        self.assertFalse(result.ready)
        self.assertEqual(result.document_id, "doc-42")

    def test_dispatch_session_save_via_package_root_returns_not_ready(self) -> None:
        result = commands.dispatch_session_save(("session-save", "doc-42", "sess-1"))
        self.assertIsInstance(result, commands.SessionSaveResult)
        self.assertFalse(result.ready)

    def test_dispatch_session_resume_via_package_root_returns_not_ready(self) -> None:
        result = commands.dispatch_session_resume(("session-resume", "sess-1"))
        self.assertIsInstance(result, commands.SessionResumeResult)
        self.assertFalse(result.ready)

    def test_dispatch_partial_command_is_exported(self) -> None:
        self.assertTrue(callable(commands.dispatch_partial_command))

    def test_unknown_command_error_type_is_exported(self) -> None:
        err = commands.UnknownCommandError(token="bad", known_tokens=("revise",))
        self.assertEqual(err.token, "bad")

    def test_partial_command_tokens_is_exported(self) -> None:
        self.assertIsInstance(commands.PARTIAL_COMMAND_TOKENS, tuple)
        self.assertEqual(len(commands.PARTIAL_COMMAND_TOKENS), 3)

    def test_dispatch_partial_command_via_package_root_routes_correctly(self) -> None:
        result = commands.dispatch_partial_command(("revise", "doc-1"))
        self.assertIsInstance(result, commands.ReviseResult)
        result = commands.dispatch_partial_command(("session-save", "doc-1", "sess-1"))
        self.assertIsInstance(result, commands.SessionSaveResult)
        result = commands.dispatch_partial_command(("session-resume", "sess-1"))
        self.assertIsInstance(result, commands.SessionResumeResult)

    def test_dispatch_partial_command_unknown_token_via_package_root(self) -> None:
        result = commands.dispatch_partial_command(("unknown",))
        self.assertIsInstance(result, commands.UnknownCommandError)

    def test_partial_command_result_type_is_exported(self) -> None:
        self.assertTrue(hasattr(commands, "PartialCommandResult"))


class StubCatalogAlignmentTests(unittest.TestCase):
    """Verify that engine_stubs.py blocker step constants stay in sync with
    catalog.py CANONICAL_DEMO_PATH_PARTIAL_COMMANDS.

    feat-engine-runs reads the blocker_step field on each result to know
    which canonical demo step it is closing. These tests ensure the strings
    in the two modules cannot drift apart silently.
    """

    def test_revise_blocker_step_is_a_canonical_partial_demo_step(self) -> None:
        partial_canonical_steps = {step for step, _ in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS}
        self.assertIn(
            REVISE_BLOCKER_STEP,
            partial_canonical_steps,
            f"REVISE_BLOCKER_STEP '{REVISE_BLOCKER_STEP}' must appear in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS",
        )

    def test_session_save_blocker_step_is_a_canonical_partial_demo_step(self) -> None:
        partial_canonical_steps = {step for step, _ in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS}
        self.assertIn(
            SESSION_SAVE_BLOCKER_STEP,
            partial_canonical_steps,
            f"SESSION_SAVE_BLOCKER_STEP '{SESSION_SAVE_BLOCKER_STEP}' must appear in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS",
        )

    def test_session_resume_blocker_step_is_a_canonical_partial_demo_step(self) -> None:
        partial_canonical_steps = {step for step, _ in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS}
        self.assertIn(
            SESSION_RESUME_BLOCKER_STEP,
            partial_canonical_steps,
            f"SESSION_RESUME_BLOCKER_STEP '{SESSION_RESUME_BLOCKER_STEP}' must appear in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS",
        )

    def test_partial_command_tokens_count_matches_canonical_partial_demo_steps(self) -> None:
        self.assertEqual(
            len(PARTIAL_COMMAND_TOKENS),
            len(CANONICAL_DEMO_PATH_PARTIAL_COMMANDS),
            "PARTIAL_COMMAND_TOKENS and CANONICAL_DEMO_PATH_PARTIAL_COMMANDS must have the same length",
        )

    def test_all_three_blocker_steps_are_covered(self) -> None:
        partial_canonical_steps = {step for step, _ in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS}
        for blocker_step in (REVISE_BLOCKER_STEP, SESSION_SAVE_BLOCKER_STEP, SESSION_RESUME_BLOCKER_STEP):
            self.assertIn(blocker_step, partial_canonical_steps)

    def test_canonical_partial_demo_steps_pins_exact_set(self) -> None:
        canonical_steps = tuple(step for step, _ in CANONICAL_DEMO_PATH_PARTIAL_COMMANDS)
        self.assertEqual(
            canonical_steps,
            (
                "produce-plan-or-revision",
                "persist-updated-document-session-state",
                "continue-without-losing-context",
            ),
        )


if __name__ == "__main__":
    unittest.main()
