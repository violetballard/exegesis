from __future__ import annotations

from src.qual.app import run
from src.qual.cli import parse_args


if __name__ == "__main__":
    cli = parse_args()
    raise SystemExit(run(project_name=cli.project))
