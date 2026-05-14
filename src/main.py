from __future__ import annotations

from src.qual.app import (
    run_bootstrap,
    run_context_basket_command,
    run_diff_preview_command,
    run_terminal_command,
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
    if cli.command == "terminal":
        return run_terminal_command(
            operation_kind=cli.terminal_operation_kind,
            message=cli.terminal_message,
            section_type=cli.terminal_section_type,
            user_intent=cli.terminal_user_intent,
            input_tokens=cli.terminal_input_tokens,
            constraints_count=cli.terminal_constraints_count,
            requires_multi_step_tools=cli.terminal_requires_multi_step_tools,
            sku_gb=cli.terminal_sku_gb,
            qwen_available=cli.terminal_qwen_available,
            runtime_supports_qwen=cli.terminal_runtime_supports_qwen,
        )
    return run_bootstrap(project_name=cli.project)


if __name__ == "__main__":
    raise SystemExit(_dispatch())
