from __future__ import annotations

import hashlib
import json
import os
import unittest
from contextlib import contextmanager

from src.qual.commands.diff_preview import (
    INCLUDE_FINGERPRINT_ENV,
    INCLUDE_SUMMARY_ENV,
    MAX_DIFF_OUTPUT_CHARS_ENV,
    OUTPUT_FORMAT_ENV,
    SUMMARY_ONLY_ENV,
    SUPPRESS_FILE_HEADERS_ENV,
    DiffPreviewInput,
    run_diff_preview,
)


@contextmanager
def _env(**updates: str | None):
    saved: dict[str, str | None] = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class DiffPreviewBehaviorTests(unittest.TestCase):
    def test_default_output_unchanged_when_env_unset(self) -> None:
        with _env(
            **{
                INCLUDE_SUMMARY_ENV: None,
                SUMMARY_ONLY_ENV: None,
                SUPPRESS_FILE_HEADERS_ENV: None,
                MAX_DIFF_OUTPUT_CHARS_ENV: None,
            }
        ):
            output = run_diff_preview(DiffPreviewInput("a
", "b
"))
        self.assertTrue(output.startswith("--- original
+++ proposed
"))
        self.assertNotIn("Diff summary:", output)

    def test_summary_counts_and_hunks_are_correct(self) -> None:
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUMMARY_ONLY_ENV: None}):
            output = run_diff_preview(DiffPreviewInput("a
old
", "a
new1
new2
"))
        self.assertTrue(output.rstrip().endswith("Diff summary: +2 -1 (hunks: 1)"))

    def test_summary_only_takes_precedence(self) -> None:
        with _env(
            **{
                SUMMARY_ONLY_ENV: "true",
                INCLUDE_SUMMARY_ENV: "1",
                MAX_DIFF_OUTPUT_CHARS_ENV: "40",
            }
        ):
            output = run_diff_preview(
                DiffPreviewInput(
                    "
".join(f"a{i}" for i in range(500)) + "
",
                    "
".join(f"b{i}" for i in range(500)) + "
",
                )
            )
        self.assertTrue(output.startswith("Diff summary: +"))
        self.assertNotIn("diff truncated", output)

    def test_header_suppression_keeps_counts_stable(self) -> None:
        base = DiffPreviewInput("a
old
", "a
new1
new2
")
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "0"}):
            output_headers = run_diff_preview(base)
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "yes"}):
            output_suppressed = run_diff_preview(base)
        self.assertTrue(output_headers.startswith("--- original
+++ proposed
"))
        self.assertFalse(output_suppressed.startswith("--- original
+++ proposed
"))
        self.assertEqual(output_headers.splitlines()[-1], output_suppressed.splitlines()[-1])

    def test_summary_only_does_not_override_no_diff_messages(self) -> None:
        with _env(**{SUMMARY_ONLY_ENV: "1"}):
            both_empty = run_diff_preview(DiffPreviewInput("", ""))
            identical = run_diff_preview(DiffPreviewInput("same
", "same
"))
        self.assertEqual(both_empty, "No diff: both inputs are empty.")
        self.assertEqual(identical, "No diff: inputs are identical after normalization.")

    def test_json_output_omits_fingerprint_when_flag_unset(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: None,
                INCLUDE_SUMMARY_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a
old
", "a
new
")))
        self.assertIsNone(payload["fingerprint"])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["summary"]["text"], "Diff summary: +1 -1 (hunks: 1)")
        self.assertIn("--- original", payload["diff"])

    def test_json_output_includes_fingerprint_object_when_flag_set(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a
", "b
")))
        self.assertEqual(payload["status"], "ok")
        self.assertIsInstance(payload["fingerprint"], dict)
        self.assertEqual(
            payload["fingerprint"]["sha256"],
            hashlib.sha256(payload["diff"].encode("utf-8")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
