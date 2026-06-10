from __future__ import annotations

from dataclasses import dataclass

from textual.widgets import Static


@dataclass(frozen=True)
class PaneCopy:
    pane_id: str
    title: str
    summary: str
    bullets: tuple[str, ...]


def render_pane_copy(copy: PaneCopy) -> str:
    bullet_lines = "\n".join(f"- {item}" for item in copy.bullets)
    return f"{copy.summary}\n\n{bullet_lines}"


class ShellPane(Static):
    can_focus = True

    def __init__(self, copy: PaneCopy) -> None:
        super().__init__(render_pane_copy(copy), id=copy.pane_id, classes="shell-pane")
        self._copy = copy

    def on_mount(self) -> None:
        self.border_title = self._copy.title


__all__ = ["PaneCopy", "ShellPane", "render_pane_copy"]
