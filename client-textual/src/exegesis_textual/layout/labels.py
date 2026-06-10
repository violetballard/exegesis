from __future__ import annotations

from rich.text import Text


def shortcut_label(chord: str, description: str) -> Text:
    label = Text()
    label.append(chord, style="#ffa62b bold")
    if description:
        label.append(f" {description}", style="bold")
    return label
