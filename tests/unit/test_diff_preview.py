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
    ORIGINAL_LABEL_ENV,
    OUTPUT_FORMAT_ENV,
    PROPOSED_LABEL_ENV,
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
            output = run_diff_preview(DiffPreviewInput("a\n", "b\n"))
        self.assertTrue(output.startswith("--- original\n+++ proposed\n"))
        self.assertNotIn("Diff summary:", output)

    def test_summary_counts_and_hunks_are_correct(self) -> None:
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUMMARY_ONLY_ENV: None}):
            output = run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew1\nnew2\n"))
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
                    "\n".join(f"a{i}" for i in range(500)) + "\n",
                    "\n".join(f"b{i}" for i in range(500)) + "\n",
                )
            )
        self.assertTrue(output.startswith("Diff summary: +"))
        self.assertNotIn("diff truncated", output)

    def test_header_suppression_keeps_counts_stable(self) -> None:
        base = DiffPreviewInput("a\nold\n", "a\nnew1\nnew2\n")
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "0"}):
            output_headers = run_diff_preview(base)
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "yes"}):
            output_suppressed = run_diff_preview(base)
        self.assertTrue(output_headers.startswith("--- original\n+++ proposed\n"))
        self.assertFalse(output_suppressed.startswith("--- original\n+++ proposed\n"))
        self.assertEqual(output_headers.splitlines()[-1], output_suppressed.splitlines()[-1])

    def test_summary_only_does_not_override_no_diff_messages(self) -> None:
        with _env(**{SUMMARY_ONLY_ENV: "1"}):
            both_empty = run_diff_preview(DiffPreviewInput("", ""))
            identical = run_diff_preview(DiffPreviewInput("same\n", "same\n"))
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
            output = run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew\n"))

        payload = json.loads(output)
        self.assertIsNone(payload["fingerprint"])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["labels"],
            {
                "applied": True,
                "original": "original",
                "proposed": "proposed",
            },
        )
        self.assertEqual(
            payload["summary"]["stats"],
            {"added": 1, "changed": 2, "hunks": 1, "net": 0, "removed": 1},
        )
        self.assertEqual(payload["summary"]["text"], "Diff summary: +1 -1 (hunks: 1)")
        self.assertIn("--- original", payload["diff"])

    def test_json_output_includes_labeled_diff_and_matching_fingerprint(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: "1",
                ORIGINAL_LABEL_ENV: "before.txt",
                PROPOSED_LABEL_ENV: "after.txt",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a\n", "b\n")))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["labels"]["original"], "before.txt")
        self.assertEqual(payload["labels"]["proposed"], "after.txt")
        self.assertTrue(payload["diff"].startswith("--- before.txt\n+++ after.txt\n"))
        self.assertEqual(
            payload["fingerprint"]["sha256"],
            hashlib.sha256(payload["diff"].encode("utf-8")).hexdigest(),
        )

    def test_json_no_diff_shape_is_stable(self) -> None:
        with _env(**{OUTPUT_FORMAT_ENV: "json"}):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(
            payload,
            {
                "diff": "",
                "fingerprint": None,
                "message": "No diff: inputs are identical after normalization.",
                "status": "no_diff",
                "summary": None,
                "summary_only": False,
                "truncated": False,
            },
        )

    def test_text_fingerprint_matches_emitted_labeled_and_truncated_diff(self) -> None:
        with _env(
            **{
                INCLUDE_FINGERPRINT_ENV: "1",
                ORIGINAL_LABEL_ENV: "old.txt",
                PROPOSED_LABEL_ENV: "new.txt",
                MAX_DIFF_OUTPUT_CHARS_ENV: "80",
            }
        ):
            output = run_diff_preview(
                DiffPreviewInput(
                    "\n".join(f"old{i}" for i in range(50)) + "\n",
                    "\n".join(f"new{i}" for i in range(50)) + "\n",
                )
            )
        diff_output, fingerprint_line = output.rsplit("\n\n", 1)
        self.assertTrue(diff_output.startswith("--- old.txt\n+++ new.txt\n"))
        self.assertEqual(
            fingerprint_line,
            f"Diff fingerprint: sha256:{hashlib.sha256(diff_output.encode('utf-8')).hexdigest()}",
        )

    def test_summary_only_json_fingerprint_matches_empty_diff_payload(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: "1",
                SUMMARY_ONLY_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a\n", "b\n")))
        self.assertEqual(payload["diff"], "")
        self.assertEqual(
            payload["fingerprint"]["sha256"],
            hashlib.sha256(b"").hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
