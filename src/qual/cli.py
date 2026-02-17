from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from src.qual.config import validate_project_name


@dataclass(frozen=True)
class CLIArgs:
    command: str
    project: str | None
    original: str | None
    proposed: str | None


def _normalize_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw:
        return ["bootstrap"]

    known = {"bootstrap", "diff-preview"}
    first = raw[0]
    # Backward compatibility: allow `--project ...` without explicit subcommand.
    if first.startswith("-"):
        return ["bootstrap", *raw]
    if first in known:
        return raw
    return raw


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    sub = parser.add_subparsers(dest="command")

    p_bootstrap = sub.add_parser("bootstrap", help="Run bootstrap shell")
    p_bootstrap.add_argument(
        "--project",
        type=validate_project_name,
        help="Project name to bootstrap under local app data directory.",
    )

    p_diff = sub.add_parser("diff-preview", help="Preview unified diff output")
    p_diff.add_argument("--original", help="Original text")
    p_diff.add_argument("--proposed", help="Proposed text")

    parser.set_defaults(command="bootstrap", project=None, original=None, proposed=None)
    ns = parser.parse_args(_normalize_argv(argv))
    return CLIArgs(
        command=str(ns.command),
        project=ns.project,
        original=ns.original,
        proposed=ns.proposed,
    )
