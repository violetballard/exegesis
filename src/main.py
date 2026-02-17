from __future__ import annotations

from src.qual.app import (
    run_bootstrap,
    run_context_basket_command,
    run_diff_preview_command,
)
from src.qual.cli import parse_args


def _dispatch() -> int:
    cli = parse_args()
    if cli.command == "diff-preview":
        return run_diff_preview_command(original=cli.original, proposed=cli.proposed)
    if cli.command == "context-basket":
        return run_context_basket_command(
            action=cli.basket_action,
            item_id=cli.basket_item_id,
        )
    return run_bootstrap(project_name=cli.project)


if __name__ == "__main__":
    raise SystemExit(_dispatch())
