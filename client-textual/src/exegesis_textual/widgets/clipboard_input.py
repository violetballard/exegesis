from __future__ import annotations

from textual.actions import SkipAction
from textual.widgets import Input

from exegesis_textual.services.clipboard import read_system_clipboard, write_system_clipboard


class SystemClipboardInput(Input):
    """Input with host OS clipboard support for packaged terminal shells."""

    def action_copy(self) -> None:
        selected_text = self.selected_text
        if not selected_text:
            raise SkipAction()
        super().action_copy()
        write_system_clipboard(selected_text)

    def action_cut(self) -> None:
        selected_text = self.selected_text
        if not selected_text:
            raise SkipAction()
        super().action_cut()
        write_system_clipboard(selected_text)

    def action_paste(self) -> None:
        clipboard = read_system_clipboard()
        if clipboard is None:
            clipboard = self.app.clipboard
        if not clipboard:
            raise SkipAction()
        start, end = self.selection
        self.replace(_single_line_clipboard_text(clipboard), start, end)


def _single_line_clipboard_text(text: str) -> str:
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").splitlines())


__all__ = ["SystemClipboardInput"]
