"""Audit utilities for context persistence.

This module provides a small helper used by the storage layer to record
audit events.  The current test suite does not exercise this functionality
directly, but it is part of the public API that other modules may import.

The audit log is simply a JSON‑lines file where each line contains a
dictionary describing an event.  ``append_audit_record`` opens the file in
``a+`` mode to avoid race conditions and writes a UTF‑8 encoded JSON string
followed by a newline.

The helper intentionally keeps dependencies minimal – only the standard
library is used, so it can be imported safely from any context without pulling
in heavy runtimes.
"""

from __future__ import annotations

import errno
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, TextIO

from exegesis_engine.context.basket import _safe_json_value
from exegesis_engine.storage._corrupt_artifacts import (
    fsync_parent_path as _fsync_parent_path,
    quarantine_corrupt_artifact,
)

# ``fold_trailing_zulu`` is intentionally not exported in ``__all__``: it is a
# shared internal recovery helper consumed by the storage modules via explicit
# import, and the canonical ``exegesis_engine.context.audit`` bridge mirrors this
# public surface, so the two ``__all__`` lists must stay identical.
__all__ = ["append_audit_record", "utc_now_iso"]


def has_trailing_zulu(candidate: str) -> bool:
    """Return whether ``candidate`` ends with a UTC zulu designator (``z``/``Z``).

    This is the single definition of "this timestamp spells its zone as a
    trailing zulu" shared by :func:`fold_trailing_zulu` (which folds the
    lowercase form so :func:`datetime.fromisoformat` can parse it) and by the
    basket store's backup-rewrite path, which keys off the same condition to
    decide whether an on-disk ``updated_at`` should be canonicalized to the
    ``+00:00`` spelling. That path previously inlined ``strip().lower().
    endswith("z")``, a case-folding one-off whose drift from this helper's notion
    of a trailing zulu is exactly the divergence the recovery consolidation work
    has been retiring. Both spellings count, since either parses to the same UTC
    instant once recovered.

    A ``z`` anywhere other than the final position does not count: it cannot be a
    valid ISO-8601 zone designator and should fail parsing rather than be folded.
    """

    return candidate.endswith(("z", "Z"))


def fold_trailing_zulu(candidate: str) -> str:
    """Fold a trailing lowercase ``z`` UTC designator to uppercase ``Z``.

    Hand-edited or legacy on-disk timestamps occasionally spell the UTC zone as
    a lowercase ``z`` (``2024-01-02T01:00:00z``). ``datetime.fromisoformat``
    rejects either ``z`` or ``Z`` outright on Python 3.9, so every recovery
    parser normalizes the suffix before parsing. They previously each inlined
    the same ``candidate[:-1] + "Z"`` slice, a defensive one-off repeated across
    the session, basket, context-set, and vault stores. Sharing one helper keeps
    that normalization identical everywhere so the same legacy timestamp recovers
    the same way regardless of which store reads it.

    Only the trailing zone designator is folded (per :func:`has_trailing_zulu`);
    a ``z`` anywhere else is left untouched, since it cannot be a valid ISO-8601
    zone and should fail parsing rather than be silently rewritten. Rewriting an
    already-uppercase ``Z`` is a no-op slice, so folding stays idempotent.
    """

    if has_trailing_zulu(candidate):
        return candidate[:-1] + "Z"
    return candidate


def parse_recovered_timestamp(value: object) -> str | None:
    """Parse an on-disk ``updated_at`` value into a canonical UTC ISO-8601 string.

    Recovery readers in several stores all need the same normalization: strip
    surrounding whitespace, fold a legacy trailing lowercase ``z`` via
    :func:`fold_trailing_zulu`, rewrite the trailing zulu designator to the
    ``+00:00`` offset that :func:`datetime.fromisoformat` accepts on Python 3.9
    (which rejects either ``z``/``Z`` outright), parse, treat a naive timestamp
    as UTC, and emit the canonical ``+00:00`` spelling. ``None`` is returned for
    non-strings, blanks, and anything ``fromisoformat`` rejects, so callers can
    treat a missing or malformed timestamp uniformly.

    This mirrors the :func:`fold_trailing_zulu` consolidation one level up: the
    document and session stores previously each inlined this identical body, and
    the basket store's copy once drifted (it dropped the fold and silently
    rejected a legacy ``...00z`` value the others accepted). Sharing one parser
    keeps recovery deterministic so the same on-disk timestamp recovers to the
    same instant regardless of which store reads it.

    The zulu-to-offset rewrite goes through :func:`has_trailing_zulu` rather than
    a blanket ``candidate.replace("Z", "+00:00")``. After folding, the only zulu
    that should remain is the trailing one this parser just normalized, and
    routing the rewrite through the same trailing-only predicate that detection
    and folding use keeps all three steps honoring one definition of a zulu
    designator. A stray ``Z`` elsewhere in the candidate is left untouched so
    ``fromisoformat`` rejects it, instead of being silently spliced into a
    spelling that might parse -- the same trailing-only invariant the recovery
    consolidation work has been pinning across the stores.
    """

    if not isinstance(value, str):
        return None
    candidate = fold_trailing_zulu(value.strip())
    if not candidate:
        return None
    if has_trailing_zulu(candidate):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO‑8601 format.

    The test suite expects timestamps with an explicit ``+00:00`` offset
    rather than a trailing ``Z``.  Earlier revisions of this function used
    :py:meth:`datetime.isoformat` followed by ``replace("+00:00", "Z")`` to
    produce the legacy ``Z`` suffix, but that broke compatibility with the
    updated tests.  Returning the raw ISO‑8601 string keeps the behaviour
    deterministic and avoids any surprises when the function is used in
    audit logs.
    """

    # ``datetime.now(timezone.utc).isoformat()`` already yields a string like
    # ``2024-04-20T12:34:56+00:00``.  No further manipulation is needed.
    return datetime.now(timezone.utc).isoformat()


def append_audit_record(log_path: Path | str, record: Dict[str, Any]) -> None:
    """Append ``record`` as a JSON line to ``log_path``.

    Parameters
    ----------
    log_path:
        Path to the audit log file.  The parent directory is created if it
        does not exist.
    record:
        Dictionary containing audit information.  It will be serialized with
        ``json.dumps``.

    Notes
    -----
    The function opens the file in text mode with UTF‑8 encoding and appends a
    newline after each JSON object.  If the directory hierarchy does not
    exist, it is created using :func:`Path.mkdir` with ``parents=True``.
    """

    path = Path(log_path)
    _prepare_audit_parent(path.parent)
    _quarantine_blocking_audit_artifact(path)
    # Serialize the record and its trailing newline into one in-memory line and
    # emit it with a single ``fh.write`` rather than streaming the body through
    # ``json.dump`` (which writes incrementally) and appending the newline as a
    # second write. Those two-plus underlying writes leave a torn-append window:
    # an interruption between the body's chunks, or between the body and its
    # newline, strands a partial record line with no terminator, and the next
    # append concatenates onto it -- merging two records into one unparseable
    # line and defeating the JSONL log's role as the forensic trail the
    # malformed-state recovery work inspects after a process interruption. A
    # single buffered write of the fully-formed line collapses that window.
    record_line = json.dumps(_safe_json_value(record), sort_keys=True) + "\n"
    # The single-write serialization above guarantees *this* writer never strands
    # a partial line, but it cannot undo a fragment already on disk: an older
    # binary that predates this hardening, an external truncation, or a torn write
    # from before the seam was pinned can leave the log ending in a record with no
    # trailing newline. An ``O_APPEND`` write lands flush against that fragment and
    # merges the two into one unparseable line, corrupting the adjacent complete
    # record as collateral and defeating the line-by-line recovery the JSONL trail
    # exists for. Terminate any such fragment with a leading newline first so it
    # stays its own (individually skippable) line and the new record lands as a
    # parseable final line. A clean log -- empty or already newline-terminated --
    # is left untouched, so the steady-state single-write shape is unchanged.
    line = record_line
    if _audit_log_lacks_final_newline(path):
        line = "\n" + record_line
    # Keep audit records byte-stable and durable so malformed-state recovery
    # can be inspected after process interruption.
    with _open_audit_append(path) as fh:
        fh.write(line)
        _fsync_audit_handle(fh)
    _fsync_audit_parent(path)


def audit_log_path(state_path: Path, store_name: str) -> Path:
    """Return the ``{store_name}_audit.jsonl`` log beside *state_path*.

    Every store's save path lands its forensic trail in a sibling of the state
    file named after the writing store class -- the basket, context-set,
    session, and vault stores each inlined the same
    ``state_path.parent / f"{self.__class__.__name__}_audit.jsonl"`` derivation
    before appending a record. Sharing one namer keeps that log-location
    contract identical across all of them, mirroring the
    ``corrupt_artifact_path_for`` and ``staged_write_temp_path``
    consolidations: the per-store ``clear`` sweeps that key on the
    ``{store_name}_audit.jsonl`` shape and the save flows that produce it now
    stay in lockstep through one definition, instead of drifting into a
    defensive one-off the next reader has to second-guess.

    ``store_name`` is the writing store's class name (``self.__class__.__name__``
    at the call sites). The append itself stays at each store module so the
    hardening tests that patch ``append_audit_record`` per module keep
    intercepting the call.
    """

    return state_path.parent / f"{store_name}_audit.jsonl"


def _audit_log_lacks_final_newline(path: Path) -> bool:
    """Return whether an existing audit log ends without its trailing newline.

    A non-empty log whose final byte is not ``\\n`` carries a stranded record
    fragment that the next ``O_APPEND`` write would merge with (see
    :func:`append_audit_record`). The probe opens the log read-only with
    ``O_NOFOLLOW`` -- mirroring :func:`_open_audit_append` -- so a raced symlink
    cannot redirect it, and reads only the trailing byte. It is best-effort: a
    missing file, a symlinked path, or any read failure means there is no
    terminated fragment to defend against (and the append path's own
    quarantine/open already guards a malformed target), so the prefix is skipped.
    """

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError:
        return False
    try:
        if os.fstat(fd).st_size == 0:
            return False
        os.lseek(fd, -1, os.SEEK_END)
        last_byte = os.read(fd, 1)
    except OSError:
        return False
    finally:
        os.close(fd)
    return last_byte not in (b"\n", b"")


def _fsync_audit_handle(fh: TextIO) -> None:
    """Flush the appended record to disk through a dedicated seam.

    Every sibling store routes its pre-finalize file flush through a named
    ``_fsync_<store>_path`` helper so hardening tests can patch the file flush
    in isolation instead of clobbering the module-global ``os.fsync`` -- which
    intercepts every fsync in the writer, the file flush *and* each
    :func:`_fsync_audit_parent` directory flush, not just the staged write. The
    audit store was the lone holdout, inlining the flush inside the append
    block. Unlike the temp-and-rename siblings (which reopen the staged temp by
    path), audit appends to a live handle that :func:`_open_audit_append`
    already opened with ``O_NOFOLLOW``; flushing that same fd keeps the
    symlink-safe descriptor rather than reintroducing a follow window by
    reopening the path read-only. Behavior is unchanged -- exactly one
    ``os.fsync`` per append, before the handle closes -- so the file flush stays
    the durability guarantee it has always been (not the best-effort flush
    :func:`_fsync_audit_parent` is) and the existing fsync-count assertions
    still hold.
    """

    fh.flush()
    os.fsync(fh.fileno())


def _quarantine_blocking_audit_artifact(path: Path) -> None:
    """Quarantine path aliases that would make audit appends unsafe."""

    if path.is_symlink() or (path.exists() and not path.is_file()):
        quarantine_corrupt_artifact(path, _audit_corrupt_path(path))


def _open_audit_append(path: Path) -> TextIO:
    """Open an audit log for append without following a raced symlink."""

    _prepare_audit_parent(path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        if exc.errno not in {errno.ELOOP, errno.ENOENT, errno.ENOTDIR, errno.EISDIR}:
            raise
        _quarantine_blocking_audit_artifact(path)
        _prepare_audit_parent(path.parent)
        fd = os.open(path, flags, 0o600)
    # ``os.fdopen`` can raise (e.g. ``OSError`` while allocating the stream
    # buffer) after the descriptor is already open. Hand ownership to the
    # ``TextIO`` wrapper only once it exists; otherwise close the raw descriptor
    # so a failed append never leaks an ``O_APPEND`` handle on the audit path.
    # Mirror :func:`session._read_session_json_text`, the canonical guard.
    try:
        handle = os.fdopen(fd, "a", encoding="utf-8")
        fd = -1
        return handle
    finally:
        if fd >= 0:
            os.close(fd)


def _prepare_audit_parent(parent: Path) -> None:
    for candidate in reversed((parent, *parent.parents)):
        # ``is_symlink`` is probed independently of ``exists`` so a *dangling*
        # symlink ancestor (one whose target is missing, for which ``exists``
        # follows the link and returns ``False``) is still quarantined. Gating the
        # symlink check behind ``exists`` would skip it, then ``mkdir`` below would
        # raise ``FileExistsError`` on the occupied name instead of recovering the
        # malformed ancestor.
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_dir()):
            quarantine_corrupt_artifact(candidate, _audit_corrupt_path(candidate))
        if not candidate.exists() and not candidate.is_symlink():
            candidate.mkdir()


def _audit_corrupt_path(path: Path) -> Path:
    if path.name.endswith(".jsonl"):
        return path.with_name(f"{path.name[:-6]}.corrupt.jsonl")
    return path.with_name(f"{path.name}.corrupt")


def _remove_live_audit_log(path: Path) -> bool:
    """Remove the live audit log on the canonical ``.jsonl`` path during a reset.

    A store's full ``clear()`` promises to leave no artifact on the audit-log
    path so the next append starts clean. A plain file or symlink is unlinked; a
    *directory* squatting on the path (a non-file alias that no append has yet
    quarantined) is removed wholesale. ``Path.unlink`` raises ``IsADirectoryError``
    on that directory, so an ``unlink``-only reset silently leaves it behind --
    ``is_clean_state`` still reports clean (the bare ``{Class}_audit.jsonl`` name
    carries no ``.corrupt.`` marker) but the *next* append quarantines the
    directory, surfacing stale state right after a deterministic reset. Mirror
    :func:`SessionStore._remove_session_clear_artifact` so every store's reset
    clears the path the same way regardless of what alias occupies it.

    On a successful removal the parent directory is fsynced so the unlink is
    durable, mirroring :func:`append_audit_record`, which always fsyncs the
    parent after writing (:func:`_fsync_audit_parent`), and
    :meth:`SessionStore.clear`, which fsyncs after removing its own audit log.
    Without it a context store's reset could remove the live audit log in the
    page cache only for the directory entry to survive a crash, resurrecting
    stale audit state after a reset the engine workflow loop treats as
    deterministic -- the same stale-state-after-reset failure this audit-log
    removal contract exists to prevent.
    """

    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
            _fsync_audit_parent(path)
            return True
        if path.is_dir():
            shutil.rmtree(path)
            _fsync_audit_parent(path)
            return True
    except (OSError, RuntimeError):
        return False
    return False


def _fsync_audit_parent(path: Path) -> None:
    # Named best-effort parent-fsync seam hardening tests patch in isolation; the
    # body is the shared :func:`_corrupt_artifacts.fsync_parent_path` so the
    # directory flush stays one audited path across all stores.
    _fsync_parent_path(path)
