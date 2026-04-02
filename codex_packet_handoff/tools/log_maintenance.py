from __future__ import annotations

import time
from pathlib import Path
from typing import Dict


def compact_log_file(path: Path, *, max_bytes: int, keep_bytes: int) -> Dict[str, int]:
    if max_bytes <= 0 or keep_bytes <= 0:
        return {"compacted": 0, "before_bytes": 0, "after_bytes": 0}
    try:
        before = path.stat().st_size
    except FileNotFoundError:
        return {"compacted": 0, "before_bytes": 0, "after_bytes": 0}
    except OSError:
        return {"compacted": 0, "before_bytes": 0, "after_bytes": 0}
    if before <= max_bytes:
        return {"compacted": 0, "before_bytes": before, "after_bytes": before}

    kept = min(keep_bytes, before)
    try:
        with path.open("rb") as fh:
            fh.seek(max(before - kept, 0))
            if before > kept:
                fh.readline()
            tail = fh.read()
    except OSError:
        return {"compacted": 0, "before_bytes": before, "after_bytes": before}

    banner = (
        f"[log compacted at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}; "
        f"kept last ~{kept} bytes of {before}]\n"
    ).encode("utf-8")
    new_bytes = banner + tail
    try:
        path.write_bytes(new_bytes)
    except OSError:
        return {"compacted": 0, "before_bytes": before, "after_bytes": before}
    return {"compacted": 1, "before_bytes": before, "after_bytes": len(new_bytes)}


def prune_log_dir(
    log_dir: Path,
    *,
    keep_recent: int,
    max_total_bytes: int,
    min_age_seconds: int,
    pattern: str = "*.log",
) -> Dict[str, int]:
    if keep_recent < 0:
        keep_recent = 0
    if max_total_bytes < 0:
        max_total_bytes = 0
    if min_age_seconds < 0:
        min_age_seconds = 0
    if not log_dir.exists():
        return {"removed": 0, "kept": 0, "bytes_before": 0, "bytes_after": 0}

    entries = []
    for path in log_dir.glob(pattern):
        try:
            st = path.stat()
        except OSError:
            continue
        if not path.is_file():
            continue
        entries.append((path, st.st_mtime, st.st_size))
    entries.sort(key=lambda item: item[1], reverse=True)
    bytes_before = sum(size for _, _, size in entries)
    total_bytes = bytes_before
    keep_set = {path for path, _, _ in entries[:keep_recent]}
    cutoff = time.time() - min_age_seconds
    removed = 0

    for path, mtime, size in reversed(entries):
        remaining = len(entries) - removed
        over_count = remaining > keep_recent
        over_bytes = total_bytes > max_total_bytes if max_total_bytes else False
        if not over_count and not over_bytes:
            break
        if path in keep_set:
            continue
        if mtime > cutoff:
            continue
        try:
            path.unlink()
        except OSError:
            continue
        removed += 1
        total_bytes -= size

    kept = max(0, len(entries) - removed)
    return {
        "removed": removed,
        "kept": kept,
        "bytes_before": bytes_before,
        "bytes_after": max(total_bytes, 0),
    }
