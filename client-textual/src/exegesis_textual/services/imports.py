from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown"}


def is_markdown_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MARKDOWN_EXTENSIONS


def path_has_hidden_part(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts if part not in {"", path.anchor})


def is_safe_markdown_import_source(path: Path) -> bool:
    try:
        resolved = path.expanduser().resolve()
    except OSError:
        return False
    return is_markdown_file(resolved) and not path_has_hidden_part(resolved)


def is_safe_external_link(href: str) -> bool:
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https"}:
        return bool(parsed.netloc)
    if parsed.scheme == "file":
        return parsed.netloc in {"", "localhost"} and bool(parsed.path)
    return False


def browseable_import_entries(directory: Path, query: str = "") -> list[Path]:
    try:
        entries = [
            entry
            for entry in directory.iterdir()
            if not entry.name.startswith(".") and (entry.is_dir() or is_markdown_file(entry))
        ]
    except OSError:
        return []
    normalized_query = query.strip().casefold()
    if normalized_query:
        entries = [entry for entry in entries if normalized_query in entry.name.casefold()]
    return sorted(entries, key=lambda entry: (entry.is_dir(), entry.name.lower()))


def importable_markdown_files_in_folder(directory: Path) -> list[Path]:
    try:
        root = directory.expanduser().resolve()
    except OSError:
        return []
    if not root.is_dir():
        return []
    results: list[Path] = []
    for path in root.rglob("*"):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if is_safe_markdown_import_source(path):
            results.append(path)
    return sorted(results, key=lambda path: str(path.relative_to(root)).casefold())
