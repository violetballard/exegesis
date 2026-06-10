from __future__ import annotations

import os
import shutil
import subprocess
import sys

_CLIPBOARD_TIMEOUT_SECONDS = 2


def read_system_clipboard() -> str | None:
    """Read the host OS clipboard, returning None when it is unavailable."""
    for command in _read_commands():
        result = _run(command)
        if result is not None:
            return result.stdout
    return None


def write_system_clipboard(text: str) -> bool:
    """Write text to the host OS clipboard when a supported tool exists."""
    for command in _write_commands():
        result = _run(command, input_text=text)
        if result is not None and result.returncode == 0:
            return True
    return False


def _run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str] | None:
    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=_CLIPBOARD_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result


def _read_commands() -> list[list[str]]:
    if sys.platform == "darwin" and shutil.which("pbpaste"):
        return [["pbpaste"]]
    if os.name == "nt":
        powershell = shutil.which("powershell.exe") or shutil.which("powershell")
        if powershell:
            return [[powershell, "-NoProfile", "-Command", "Get-Clipboard -Raw"]]
    commands: list[list[str]] = []
    if shutil.which("wl-paste"):
        commands.append(["wl-paste", "--no-newline"])
    if shutil.which("xclip"):
        commands.append(["xclip", "-selection", "clipboard", "-out"])
    if shutil.which("xsel"):
        commands.append(["xsel", "--clipboard", "--output"])
    return commands


def _write_commands() -> list[list[str]]:
    if sys.platform == "darwin" and shutil.which("pbcopy"):
        return [["pbcopy"]]
    if os.name == "nt":
        powershell = shutil.which("powershell.exe") or shutil.which("powershell")
        if powershell:
            return [[powershell, "-NoProfile", "-Command", "Set-Clipboard -Value ([Console]::In.ReadToEnd())"]]
    commands: list[list[str]] = []
    if shutil.which("wl-copy"):
        commands.append(["wl-copy"])
    if shutil.which("xclip"):
        commands.append(["xclip", "-selection", "clipboard"])
    if shutil.which("xsel"):
        commands.append(["xsel", "--clipboard", "--input"])
    return commands


__all__ = ["read_system_clipboard", "write_system_clipboard"]
