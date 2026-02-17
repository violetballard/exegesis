from __future__ import annotations

import argparse
from dataclasses import dataclass

from src.qual.config import validate_project_name


@dataclass(frozen=True)
class CLIArgs:
    project: str | None


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    parser.add_argument(
        "--project",
        type=validate_project_name,
        help="Project name to bootstrap under local app data directory.",
    )
    ns = parser.parse_args(argv)
    return CLIArgs(project=ns.project)
