from __future__ import annotations

import base64
import json
import os
import shutil
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import BinaryIO, Callable
from uuid import uuid4

_STRIPPED_SNAPSHOT_PATH_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})

# Windows reserves these device names: a path component whose base name (the
# text before its first dot, with trailing dots/spaces stripped) matches one --
# case-insensitively -- names a device, not a regular file, no matter the
# extension. ``CON``, ``CON.txt``, and ``con.log`` all open the console device.
#
# Windows path canonicalization also treats the superscript-digit spellings
# ``COM¹``/``COM²``/``COM³`` and ``LPT¹``/``LPT²``/``LPT³`` (U+00B9/U+00B2/U+00B3)
# as the matching ``COM1``-``COM3``/``LPT1``-``LPT3`` devices. Those code points
# are category ``No`` (so the Cc/Cf/Zl/Zp filter misses them) and casefold to
# themselves, so ``com¹`` keys distinctly from ``com1`` and would survive every
# per-entry, casefold, and ancestor/overlap check, then collide on one device
# during restore -- or a single ``COM¹`` entry simply fails to materialize the
# intended POSIX file. Fold these spellings in so they reject alongside their
# ASCII forms.
_WINDOWS_RESERVED_DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{digit}" for digit in range(1, 10)}
    | {f"lpt{digit}" for digit in range(1, 10)}
    | {f"com{sup}" for sup in ("¹", "²", "³")}
    | {f"lpt{sup}" for sup in ("¹", "²", "³")}
)

_DIRECTORY_SNAPSHOT_MARKER = b"__QUAL_CORRUPT_DIR__\n"
_MAX_CORRUPT_PATH_CANDIDATES = 10000


def is_reserved_windows_device_base(component: str) -> bool:
    """Return ``True`` when a single path component names a Windows device.

    Windows resolves a component to a reserved device when its base name -- the
    text before the first dot, with trailing spaces stripped, compared
    case-insensitively -- is one of ``CON``, ``PRN``, ``AUX``, ``NUL``,
    ``COM1``-``COM9``, or ``LPT1``-``LPT9`` (plus the superscript ``COM¹``/``LPT¹``
    spellings folded in :data:`_WINDOWS_RESERVED_DEVICE_NAMES`). The extension is
    irrelevant: ``CON``, ``CON.txt``, and ``con.log`` all open the console device.

    This is the single definition of "this component names a reserved device"
    shared by the snapshot-path gate (:func:`_is_safe_snapshot_relative_path`,
    which drops a colliding snapshot entry) and by the vault's
    :func:`~qual.storage.vault.validate_project_name` (which rejected reserved
    project names through its own uppercase-membership copy). Both layers reject
    the same base name the same way, so a name that cannot become a vault
    directory also cannot survive as a snapshot entry -- the divergence-retiring
    consolidation this storage floor has been applying to its other one-off
    recovery helpers.
    """

    return component.split(".", 1)[0].rstrip(" ").casefold() in _WINDOWS_RESERVED_DEVICE_NAMES


def _is_safe_snapshot_relative_path(relative_path: str) -> bool:
    """Return ``True`` when a snapshot entry stays within the corrupt root."""

    if not isinstance(relative_path, str) or not relative_path:
        return False
    if "\\" in relative_path:
        # Snapshot payloads are serialized with POSIX separators. Reject raw
        # backslashes so a path entry cannot mean one thing on POSIX and a
        # different path on Windows during restore.
        return False
    if ":" in relative_path:
        # A colon is a literal filename character on POSIX, but on Windows NTFS
        # it designates an alternate data stream: restoring ``data.txt:s`` would
        # not create that standalone sibling -- it would write a hidden stream
        # onto ``data.txt`` (materializing an empty ``data.txt`` if absent),
        # silently aliasing the base name and dropping the intended entry. Like
        # a raw backslash, a colon makes a path mean a plain file on POSIX and
        # something categorically different on Windows during restore, so reject
        # it at the gate. Dropping the single colon-bearing entry keeps the
        # readable rest of the artifact recoverable and consistent across
        # platforms, the same tradeoff the dots/spaces-only rejection makes.
        return False
    posix_candidate = PurePosixPath(relative_path)
    if posix_candidate.as_posix() != relative_path:
        # Reject alternate spellings such as ``a//b`` and ``a/./b``. They
        # normalize to the same target as ``a/b`` and can otherwise bypass the
        # raw duplicate-path check below.
        return False
    if any(unicodedata.category(ch) in _STRIPPED_SNAPSHOT_PATH_CATEGORIES for ch in relative_path):
        return False
    for candidate in (posix_candidate, PureWindowsPath(relative_path)):
        if candidate.is_absolute() or candidate.drive:
            return False
        if not candidate.parts:
            return False
        if any(not part.rstrip(". ") for part in candidate.parts):
            # Reject ``.``/``..``/empty parts and any component made up solely of
            # dots and spaces (e.g. ``...`` or ``"   "``). Windows strips trailing
            # dots and spaces from every component, so such a component has no
            # representation there at all -- it collapses to nothing rather than
            # aliasing a sibling. ``_snapshot_casefold_key`` folds it to an empty
            # path segment, and restore would fail closed on the whole snapshot;
            # dropping it at the gate keeps the readable rest recoverable.
            return False
        if any(is_reserved_windows_device_base(part) for part in candidate.parts):
            # A component naming a Windows reserved device (``CON``, ``NUL``,
            # ``COM1`` ...) -- with or without an extension -- opens the device
            # rather than creating the intended sibling file there. Like the
            # colon and backslash cases, the path means a plain file on POSIX and
            # something categorically different on Windows: ``CON`` and ``CON.txt``
            # both resolve to one device and would survive every per-entry,
            # casefold, and ancestor/overlap check, then collide (or fail to
            # materialize) during restore. Reject it at the shared gate so the
            # emitter drops the single entry and restore fails closed before any
            # filesystem mutation, the same cross-platform tradeoff the
            # dots/spaces-only and colon rejections make.
            return False
    return True


def _snapshot_paths_conflict(left: str, right: str) -> bool:
    """Return ``True`` when two snapshot entries would collide on disk."""

    left_path = PurePosixPath(left)
    right_path = PurePosixPath(right)
    return left_path == right_path or left_path in right_path.parents or right_path in left_path.parents


def _snapshot_casefold_key(relative_path: str) -> str:
    """Return a filesystem-agnostic key for detecting case and Unicode aliases.

    Casefolding alone collapses only case differences. Normalization-insensitive
    filesystems (macOS APFS/HFS+) also treat the composed and decomposed spellings
    of the same name -- e.g. NFC ``é`` (U+00E9) versus NFD ``e`` + U+0301 -- as one
    file. Two snapshot entries differing only by Unicode normalization form would
    otherwise survive both the per-entry alias check and the ancestor/overlap
    conflict checks, then collapse onto a single target during restore: the second
    ``open("xb")`` raises ``FileExistsError`` and the whole artifact fails closed,
    discarding recoverable state. Normalizing to NFC -- before and after casefold,
    since casefolding can itself denormalize -- folds those spellings together so
    the collision is caught the same way a case alias is. Pure-ASCII paths are
    unaffected (they are already NFC and casefold-stable).

    Windows applies the same collapse for a different reason: it strips trailing
    dots and spaces from every path component, so ``data.txt``, ``data.txt.``, and
    ``data.txt `` all open the same file. Two snapshot entries differing only by
    trailing dots/spaces would survive the checks above and then collide on the
    second ``open("xb")`` during restore -- the same fail-closed-on-the-whole-
    artifact loss the case and normalization aliasing fixes prevent. Stripping
    trailing ``.``/`` `` from each folded component closes that alias too. A
    component made up solely of dots/spaces (which would fold to an empty key)
    is rejected earlier by ``_is_safe_snapshot_relative_path``, since it has no
    representation on Windows at all. Paths without trailing dots/spaces are
    unaffected.
    """

    folded = PureWindowsPath(relative_path).as_posix()
    folded = unicodedata.normalize("NFC", folded).casefold()
    folded = unicodedata.normalize("NFC", folded)
    return "/".join(component.rstrip(". ") for component in folded.split("/"))


def _snapshot_file_directory_conflict(file_path: str, directory_path: str) -> bool:
    """Return ``True`` when a file entry would block a directory entry."""

    file_candidate = PurePosixPath(file_path)
    directory_candidate = PurePosixPath(directory_path)
    return file_candidate == directory_candidate or file_candidate in directory_candidate.parents


def is_directory_snapshot_bytes(data: bytes) -> bool:
    return data.startswith(_DIRECTORY_SNAPSHOT_MARKER)


def snapshot_corrupt_artifact_bytes(path: Path) -> bytes | None:
    """Return the persisted bytes for a corrupt artifact or directory snapshot."""

    if path.is_symlink():
        # Never snapshot a symlink by following its target. If the move-based
        # quarantine path fails, treating the symlink as a plain file would
        # leak the target's bytes into the quarantine artifact.
        return None
    if path.is_dir() and not path.is_symlink():
        entries: list[dict[str, str]] = []
        seen_relative_paths: set[str] = set()
        seen_casefold_paths: set[str] = set()
        # Track ancestor/overlap conflicts on casefolded keys so the emitter
        # mirrors the restore-time conflict checks. Emitting an exact-case
        # snapshot that only ``restore_corrupt_artifact_bytes`` rejects (via its
        # casefolded checks) would fail closed on the whole artifact instead of
        # dropping the single conflicting entry here, discarding the readable
        # rest. The emitted entry dicts still carry the original relative path.
        directory_entries: set[str] = set()
        file_entries: set[str] = set()
        try:
            def _snapshot_sort_key(candidate: Path) -> tuple[int, str]:
                try:
                    return (0, str(candidate.relative_to(path)))
                except ValueError:
                    return (1, str(candidate))

            for entry in sorted(path.rglob("*"), key=_snapshot_sort_key):
                if entry.is_symlink():
                    # Symlinks can point outside the quarantined tree.
                    # Snapshotting them would leak unrelated state into the
                    # corrupt-artifact payload, so skip them and keep the
                    # snapshot rooted inside the quarantined directory.
                    continue
                try:
                    relative_path = entry.relative_to(path).as_posix()
                except ValueError:
                    # Filesystem walks should stay under ``path``. If a raced
                    # or monkeypatched walk surfaces an escaped entry, preserve
                    # the rest of the corrupt artifact without snapshotting
                    # data outside the quarantine root.
                    continue
                if relative_path in seen_relative_paths:
                    # Some filesystem walks can surface the same logical path
                    # more than once via aliasing or monkeypatched test
                    # fixtures. Keep the emitted snapshot self-consistent by
                    # ignoring duplicate relative paths instead of generating
                    # a restore payload that would fail closed later.
                    continue
                if not _is_safe_snapshot_relative_path(relative_path):
                    continue
                casefold_path = _snapshot_casefold_key(relative_path)
                if casefold_path in seen_casefold_paths:
                    # Match restore-time collision checks while preserving the
                    # rest of the corrupt artifact. A case alias would make the
                    # snapshot fail closed on case-insensitive filesystems.
                    continue
                try:
                    is_dir = entry.is_dir()
                except OSError:
                    continue
                if is_dir:
                    if any(
                        _snapshot_file_directory_conflict(file_path, casefold_path)
                        for file_path in file_entries
                    ):
                        continue
                    entries.append({"kind": "dir", "path": relative_path})
                    seen_relative_paths.add(relative_path)
                    seen_casefold_paths.add(casefold_path)
                    directory_entries.add(casefold_path)
                    continue
                try:
                    is_file = entry.is_file()
                except OSError:
                    continue
                if not is_file:
                    continue
                if any(_snapshot_paths_conflict(file_path, casefold_path) for file_path in file_entries):
                    continue
                if any(
                    _snapshot_file_directory_conflict(casefold_path, directory_path)
                    for directory_path in directory_entries
                ):
                    continue
                try:
                    raw_bytes = entry.read_bytes()
                except OSError:
                    # Preserve the rest of the directory snapshot even when
                    # one nested file cannot be read. A partially unreadable
                    # corrupt tree is still worth snapshotting so recovery can
                    # restore the readable portion instead of discarding the
                    # whole artifact.
                    continue
                entries.append(
                    {
                        "kind": "file",
                        "path": relative_path,
                        "content": base64.b64encode(raw_bytes).decode("ascii"),
                    }
                )
                seen_relative_paths.add(relative_path)
                seen_casefold_paths.add(casefold_path)
                file_entries.add(casefold_path)
        except OSError:
            return None
        payload = json.dumps(entries, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return _DIRECTORY_SNAPSHOT_MARKER + payload
    try:
        return path.read_bytes()
    except OSError:
        return None


def restore_corrupt_artifact_bytes(corrupt_path: Path, data: bytes) -> bool:
    """Restore a corrupt directory snapshot encoded by this module."""

    if not is_directory_snapshot_bytes(data):
        return False
    try:
        payload = json.loads(data[len(_DIRECTORY_SNAPSHOT_MARKER) :].decode("utf-8"))
    except Exception:
        return False
    if not isinstance(payload, list):
        return False

    directory_entries: list[str] = []
    file_entries: list[tuple[str, bytes]] = []
    seen_relative_paths: set[str] = set()
    seen_casefold_paths: set[str] = set()
    for entry in payload:
        if not isinstance(entry, dict):
            return False
        relative_path = entry.get("path")
        kind = entry.get("kind")
        if not isinstance(relative_path, str) or not isinstance(kind, str):
            return False
        if not _is_safe_snapshot_relative_path(relative_path):
            return False
        if relative_path in seen_relative_paths:
            # Conflicting snapshot entries should fail closed before any
            # filesystem mutation happens. The snapshot format emitted by this
            # module is unique by construction, so duplicates signal malformed
            # or hostile data rather than a recoverable directory tree.
            return False
        seen_relative_paths.add(relative_path)
        casefold_path = _snapshot_casefold_key(relative_path)
        if casefold_path in seen_casefold_paths:
            # Case-insensitive filesystems would collapse these entries into a
            # single target. Reject the snapshot instead of letting restore
            # order decide which corrupt artifact survives.
            return False
        seen_casefold_paths.add(casefold_path)
        if kind == "dir":
            directory_entries.append(relative_path)
            continue
        if kind != "file":
            return False
        content = entry.get("content")
        if not isinstance(content, str):
            return False
        try:
            raw_bytes = base64.b64decode(content.encode("ascii"), validate=True)
        except Exception:
            return False
        file_entries.append((relative_path, raw_bytes))

    # Detect ancestor/overlap conflicts on casefolded paths. The per-entry
    # case-alias rejection above only catches whole-path duplicates, so a file
    # and directory (or two files) that collide only by case across a parent
    # boundary -- e.g. directory ``Logs`` and file ``logs/data.txt`` -- would
    # otherwise pass validation here yet merge into a single target on a
    # case-insensitive filesystem during restore. Casefolding the conflict
    # checks subsumes the exact-case comparison (equal paths stay equal once
    # folded) while failing closed on these cross-case collisions before any
    # filesystem mutation happens.
    directory_casefold = [_snapshot_casefold_key(path) for path in directory_entries]
    directory_casefold_set = set(directory_casefold)
    file_paths_casefold = [
        _snapshot_casefold_key(relative_path) for relative_path, _raw_bytes in file_entries
    ]
    for file_path in file_paths_casefold:
        if file_path in directory_casefold_set:
            return False
        for directory_path in directory_casefold:
            if _snapshot_file_directory_conflict(file_path, directory_path):
                return False
    for index, left_path in enumerate(file_paths_casefold):
        for right_path in file_paths_casefold[index + 1 :]:
            if _snapshot_paths_conflict(left_path, right_path):
                return False

    try:
        if corrupt_path.exists() or corrupt_path.is_symlink():
            _remove_path(corrupt_path)
        corrupt_path.mkdir(parents=True, exist_ok=True)
        # The pre-restore wipe above is best-effort: ``_remove_path`` swallows the
        # filesystem rejection a constrained runtime can raise. When the surviving
        # entry is a symlink to a directory, the ``exist_ok=True`` mkdir follows it
        # and silently succeeds, so the root itself stays an alias pointing outside
        # the quarantine tree. The per-entry ``_reject_restored_symlink_alias``
        # guard only inspects path components *under* the root, never the root, and
        # the emptiness probe below follows the alias to the target's contents --
        # so without this check the snapshot files would be written straight
        # through the alias into the external target, the exact escape symlink
        # hardening exists to prevent. Fail closed before probing or writing any
        # content if the recreated root is a symlink; the rollback path unlinks the
        # alias without following it.
        if corrupt_path.is_symlink():
            raise OSError(f"corrupt artifact root is a symlink before restore: {corrupt_path!r}")
        # The pre-restore wipe is likewise best-effort against a stale *real* tree.
        # A stale entry left by an earlier interrupted restore would otherwise
        # persist alongside the freshly written snapshot entries -- any leftover
        # file the snapshot does not itself overwrite stays behind, so the
        # restored tree becomes a merge of old and new state rather than a
        # faithful image of the snapshot, defeating the forensic determinism this
        # recovery path exists to guarantee. Fail closed before writing any
        # snapshot content if the recreated root is not empty, so a restore that
        # could not start from a clean tree reports failure instead of producing a
        # stale/snapshot hybrid.
        if any(corrupt_path.iterdir()):
            raise OSError(f"corrupt artifact root not empty before restore: {corrupt_path!r}")
        for relative_path in sorted(directory_entries):
            restored_directory = corrupt_path / Path(relative_path)
            # Mirror the file loop below, which rejects a symlinked ancestor
            # *before* writing any content. ``mkdir(parents=True)`` follows a
            # symlinked ancestor and creates the new directory inside the alias
            # target, so checking only after the mkdir (as before) lets a parent
            # raced into a symlink between iterations leak a directory into the
            # external target before the guard fires -- and rollback's
            # ``_remove_path`` unlinks the alias without following it, so that
            # leaked directory is never cleaned up. Reject a symlinked ancestor
            # before creating anything through it.
            _reject_restored_symlink_alias(corrupt_path, restored_directory.parent)
            restored_directory.mkdir(parents=True, exist_ok=True)
            # The final component can still be raced into a symlink by the mkdir
            # itself, so keep the post-mkdir check on the full restored path.
            _reject_restored_symlink_alias(corrupt_path, restored_directory)
            _fsync_parent(restored_directory)
        for relative_path, raw_bytes in sorted(file_entries, key=lambda item: item[0]):
            target = corrupt_path / Path(relative_path)
            # Mirror the directory loop's pre/post symlink-alias guard. A file
            # whose parent is not also carried as its own ``dir`` snapshot entry
            # is first materialized by this ``mkdir`` (``_write_restored_file`` no
            # longer creates it), and ``mkdir(parents=True)`` follows a symlinked
            # ancestor. Checking only *before* the mkdir -- as before, when the
            # mkdir lived unguarded inside ``_write_restored_file`` -- lets a
            # parent component raced into an alias between the pre-check and the
            # mkdir (or by the mkdir itself) carry the staged write below straight
            # through the alias into the external target. The pre-check rejects a
            # pre-existing alias; the post-mkdir check rejects one raced in while
            # the parent was being created, before any content is written.
            _reject_restored_symlink_alias(corrupt_path, target.parent)
            target.parent.mkdir(parents=True, exist_ok=True)
            _reject_restored_symlink_alias(corrupt_path, target.parent)
            _write_restored_file(target, raw_bytes)
            _fsync_parent(target.parent)
            _fsync_parent(target)
        _fsync_parent(corrupt_path)
    except (OSError, RuntimeError):
        # Leave no partially restored tree behind when a malformed snapshot
        # collides with the filesystem layout during recovery.
        _remove_path_and_fsync_parent(corrupt_path)
        return False
    return True


def restore_corrupt_artifact_snapshots(
    snapshots: tuple[tuple[Path, bool, bytes | None], ...],
    write_bytes: Callable[[Path, bytes], None],
    *,
    unlink_symlinks: bool = False,
) -> None:
    """Re-publish corrupt-artifact snapshots captured before a recovery rollback.

    This is the canonical restore loop shared by the vault, basket, and
    context-set stores. Each store previously carried its own near-identical
    copy of this body; the only real differences were the store-specific
    content-flushing writer (passed in as *write_bytes*) and whether a stale
    symlink standing on the corrupt path should be cleared first.

    Restore is best-effort: a snapshot whose live forensic copy reappeared, or
    one that never captured bytes, is skipped, and a writer that fails leaves
    the slot empty rather than republishing a torn artifact. Directory
    snapshots are rehydrated through :func:`restore_corrupt_artifact_bytes`,
    which carries its own atomic write + parent flush; plain byte payloads go
    through *write_bytes* so they share the same content-flush seam as
    canonical state instead of a raw, unflushed ``write_bytes``.
    """

    for corrupt_path, _, data in snapshots:
        if unlink_symlinks and corrupt_path.is_symlink():
            try:
                corrupt_path.unlink()
            except OSError:
                pass
        if data is None or corrupt_path.exists():
            continue
        if is_directory_snapshot_bytes(data):
            restore_corrupt_artifact_bytes(corrupt_path, data)
            continue
        try:
            write_bytes(corrupt_path, data)
        except (OSError, ValueError):
            pass


def state_root_uses_symlink_alias(path: Path) -> bool:
    """Return ``True`` when any component of *path* is a symlink alias.

    Walks every component from the leaf up to the filesystem anchor, treating an
    inspection failure as an alias so the guard fails closed. Components that sit
    directly beneath the anchor (e.g. ``/var``) are skipped so platform aliases
    such as macOS ``/var -> /private/var`` do not reject every state root. This is
    the canonical state-root alias guard shared by the vault, session, basket, and
    context-set stores so a swapped-in symlink root is rejected identically across
    all engine persistence floors.
    """

    candidate = path
    while candidate != candidate.parent:
        try:
            if candidate.is_symlink() and candidate.parent != Path(candidate.anchor):
                return True
        except (OSError, RuntimeError):
            return True
        candidate = candidate.parent
    return False


def _reject_restored_symlink_alias(root: Path, path: Path) -> None:
    """Fail closed if a restored snapshot path crosses a symlink alias."""

    try:
        relative_path = path.relative_to(root)
    except ValueError as exc:
        raise OSError(f"restored path escapes corrupt artifact root: {path!r}") from exc
    current_path = root
    for part in relative_path.parts:
        current_path = current_path / part
        if current_path.is_symlink():
            raise OSError(f"restored path uses a symlink alias: {path!r}")


def _remove_path(path: Path) -> None:
    try:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()
    except (OSError, RuntimeError):
        # Removal here is best-effort cleanup: clearing a stale target before a
        # snapshot restore (``restore_corrupt_artifact_bytes``) or rolling back a
        # partial atomic write (``_remove_path_and_fsync_parent``). A constrained
        # runtime can surface a filesystem rejection as ``RuntimeError`` rather than
        # ``OSError``; letting that propagate would crash an already-best-effort
        # cleanup -- and at the atomic-write rollback site it would mask the real
        # ``OSError`` being re-raised -- forcing the engine workflow loop into the
        # defensive one-off repair this storage floor exists to remove.
        pass


def _remove_path_and_fsync_parent(path: Path) -> None:
    _remove_path(path)
    try:
        _fsync_parent(path)
    except OSError:
        pass


def _write_restored_file(path: Path, data: bytes) -> None:
    """Stage a restored snapshot file through a temp + atomic rename.

    Every other content writer on this storage floor -- the temp-and-rename
    document/session/vault/context-set writers and the sibling
    :func:`_write_corrupt_bytes_atomic` -- lands bytes at a canonical path only
    after a fully flushed staged temp is atomically renamed into place, so an
    interrupted write can never leave a half-written file at the final name. The
    directory-snapshot restore writer was the lone holdout, opening the final
    ``path`` directly with ``"xb"``: a torn write there would strand a partially
    written file at its restored name inside the forensic tree, where it
    masquerades as a complete recovered entry and defeats the snapshot's audit
    purpose. Stage to a sibling temp, flush its content through
    :func:`_fsync_corrupt_handle`, then atomically rename, cleaning up the staged
    temp if the write fails before the rename lands.
    """

    # The caller materializes ``path.parent`` under a pre/post symlink-alias
    # guard before invoking this writer, so the parent already exists and has
    # been validated as a real directory inside the quarantine tree. Recreating
    # it here with an unguarded ``mkdir(parents=True)`` would reopen the exact
    # symlinked-ancestor race the caller's post-mkdir check just closed -- a
    # parent raced into an alias would be silently followed and the staged write
    # below would land through it -- so the parent is left to the guarded caller.
    # Stage through a uuid-suffixed sibling temp rather than a fixed
    # ``<name>.tmp``. The snapshot being restored can legitimately carry a
    # sibling entry named exactly ``<name>.tmp`` -- a corrupt tree may hold both
    # a file ``data`` and a directory ``data.tmp``, and directory entries are
    # materialized before files. A fixed temp name then aliases that real entry:
    # the exclusive ``"xb"`` open fails on the existing directory, and the
    # rollback ``_remove_path`` below would delete the legitimate restored
    # sibling before re-raising -- turning a faithful, restorable snapshot into a
    # whole-artifact failure and silently dropping a recovered entry. A uuid
    # suffix cannot alias any snapshot entry, so staging never collides and
    # rollback only ever removes this write's own temp.
    tmp_path = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
    try:
        with tmp_path.open("xb") as file:
            file.write(data)
            _fsync_corrupt_handle(file)
        os.replace(tmp_path, path)
    except OSError:
        _remove_path(tmp_path)
        raise


def _fsync_corrupt_handle(file: BinaryIO) -> None:
    """Flush a staged corrupt-artifact write to disk through a dedicated seam.

    Every sibling store routes its pre-finalize file flush through a named
    helper (``_fsync_<store>_path`` for the temp-and-rename writers,
    :func:`~qual.context.audit._fsync_audit_handle` for the live-handle audit
    append) so hardening tests can patch the file flush in isolation instead of
    clobbering the module-global ``os.fsync`` -- which intercepts every fsync in
    the writer, the staged content flush *and* each :func:`_fsync_parent`
    directory flush, not just the write under test. The corrupt-artifact writers
    were the lone holdout, inlining the flush inside their ``with`` blocks. Like
    the audit append (and unlike the temp-and-rename siblings that reopen the
    staged temp by path), these flush a live handle still open inside the block,
    so the seam takes the handle and flushes that same descriptor. Behavior is
    unchanged -- exactly one ``os.fsync`` per staged write, before the handle
    closes -- so the file flush stays the durability guarantee it has always
    been (not the best-effort flush :func:`_fsync_parent` is) and a rejected
    flush still propagates: a torn quarantine write never reports success.
    """

    file.flush()
    os.fsync(file.fileno())


def fsync_file_path(path: Path) -> None:
    """Flush an already-written file to disk by reopening it read-only.

    This is the canonical body behind every store's ``_fsync_<store>_path``
    content-flush seam (basket, context-set, session, vault, document). Those
    writers stage a temp, close it, then reopen it here to fsync the persisted
    bytes before the atomic replace -- the durability guarantee, distinct from
    the best-effort :func:`_fsync_parent` directory flush. Each store keeps its
    own named seam so hardening tests can patch the flush in isolation; the seam
    now delegates here instead of carrying a byte-identical copy, so the flush
    stays one audited path rather than five divergence risks. A rejected flush
    still propagates: a torn store write never reports success.
    """

    with path.open("rb") as file:
        os.fsync(file.fileno())


def fsync_directory_path(directory: Path) -> None:
    """Best-effort flush of a *directory* entry to disk.

    This is the canonical body behind every store's best-effort directory
    flush: both the ``_fsync_<store>_parent`` rename-durability seams (basket,
    context-set, session, vault, audit) via :func:`fsync_parent_path`, and the
    document store's ``_fsync_directory`` -- the last directory-flush body that
    still carried its own copy. Opening with ``O_DIRECTORY`` when the platform
    exposes it keeps the flush from ever fsync-ing a non-directory; platforms
    without it fall back to a plain ``O_RDONLY`` open (``getattr`` yields ``0``),
    matching the open the parent-flush seam used before this consolidation.

    Unlike :func:`fsync_file_path`, this is best-effort: it sits on top of an
    already-completed unlink/rename, opening the directory is best-effort, and so
    the flush is too. Some filesystems reject a directory fsync with ``OSError``
    (``EINVAL``), and a constrained runtime can surface the same rejection as
    ``RuntimeError``; letting either propagate would turn the hardening into a
    hard failure of an operation that already succeeded in the page cache,
    forcing the engine workflow loop into the defensive one-off repair this
    storage floor exists to remove. The directory fd is always closed.
    """

    try:
        directory_fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except (OSError, RuntimeError):
        return
    try:
        os.fsync(directory_fd)
    except (OSError, RuntimeError):
        return
    finally:
        os.close(directory_fd)


def fsync_parent_path(path: Path) -> None:
    """Best-effort flush of *path*'s parent directory entry to disk.

    This is the canonical body behind every store's ``_fsync_<store>_parent``
    seam (basket, context-set, session, vault, audit). Those writers stage a
    temp, fsync its bytes (the durability guarantee, via
    :func:`fsync_file_path`), then atomically rename it into place; this layers
    a best-effort directory flush on top so the rename entry itself reaches
    disk. Each store keeps its own named seam so hardening tests can patch the
    flush in isolation; the seam now delegates here instead of carrying a
    byte-identical copy, so the directory flush stays one audited path rather
    than five divergence risks.

    The flush itself lives in :func:`fsync_directory_path`, shared with the
    document store's ``_fsync_directory`` so every best-effort directory flush --
    rename-parent and directory-create alike -- runs one audited body.
    """

    fsync_directory_path(path.parent)


def _fsync_parent(path: Path) -> None:
    # Internal alias preserved for in-module callers and the corrupt-artifact
    # hardening tests that patch this seam; delegates to the public canonical
    # :func:`fsync_parent_path` so the best-effort directory flush stays one body.
    fsync_parent_path(path)


def staged_write_temp_path(path: Path) -> Path:
    """Return the hidden, per-write staged temp name for an atomic content write.

    The document store (``project_store``) and the vault store each staged a
    fresh content write under ``.{name}.{uuid}.tmp`` -- a leading dot to hide the
    in-progress temp from directory listings and a uuid so two concurrent writers
    never collide on the same staged name -- then atomically renamed it into
    place. Sharing one namer keeps that staged-write contract identical across
    both stores, mirroring the ``fsync_file_path`` and ``corrupt_artifact_path_for``
    consolidations: the per-store stale-temp sweeps that quarantine interrupted
    writes match against this exact ``.{name}.{uuid}.tmp`` shape, so the namer and
    the sweep stay in lockstep through one definition. The sibling corrupt-artifact
    writer (:func:`_write_corrupt_bytes_atomic`) keeps its own undotted, single
    ``{name}.tmp`` temp inside the forensic tree and is intentionally not routed
    through here.
    """

    return path.with_name(f".{path.name}.{uuid4().hex}.tmp")


def legacy_json_temp_path(path: Path) -> Path:
    """Return the legacy ``{stem}.tmp.json`` staged-temp sibling of a state path.

    Older writers in the basket and context-set stores staged temp state under
    ``{stem}.tmp.json`` rather than the collapsed ``{stem}.tmp`` that
    ``path.with_suffix(".tmp")`` now produces. An interrupted legacy write leaves
    that sibling stranded on disk, so both stores derive this name to stale-
    quarantine the leftover the way the canonical ``.tmp`` is handled. Sharing one
    namer keeps the legacy-temp shape identical across both stores, mirroring the
    ``staged_write_temp_path`` and ``corrupt_artifact_path_for`` consolidations:
    the per-store legacy-family ``clear`` sweeps that key on this exact
    ``{stem}.tmp.json`` shape and the save-flow quarantine that produces it now
    stay in lockstep through one definition.
    """

    return path.with_name(f"{path.stem}.tmp.json")


def staged_atomic_write(
    path: Path,
    content: str | bytes,
    *,
    encoding: str | None,
    quarantine_blocking: Callable[[Path], None],
    quarantine_stale_temp: Callable[[Path], None],
    fsync_content: Callable[[Path], None],
    fsync_parent: Callable[[Path], None],
    remove_temp: Callable[[Path], None],
    symlink_label: str,
) -> None:
    """Stage *content* to a ``{stem}.tmp`` sibling and atomically replace *path*.

    The basket and context-set stores each landed both their canonical payload
    writes and their verbatim forensic-snapshot byte restores through the same
    body: create the parent, quarantine any blocking artifact at the target and
    any stale temp left by an interrupted write, write the staged temp, flush its
    content, reject a temp that raced into a symlink, atomically ``replace`` it
    into place, then flush the parent directory -- cleaning the staged temp on any
    ``OSError`` so a torn write never strands a half-written sibling that the next
    write's stale-temp sweep would preserve as masquerading-corrupt noise. The two
    stores differed only in their named per-store seams (which hardening tests
    patch in isolation) and the symlink-rejection label, so both pairs delegate
    here with those seams passed in, mirroring the ``fsync_file_path`` and
    ``legacy_json_temp_path`` consolidations: one audited atomic-write body the
    engine loop can rely on for deterministic, recoverable state.

    Text payloads pass ``encoding="utf-8"`` (opening the temp in ``"x"`` text
    mode); verbatim byte restores pass ``encoding=None`` (binary ``"xb"``) so the
    quarantined bytes are republished without re-encoding.
    """

    tmp = path.with_suffix(".tmp")
    mode = "x" if encoding is not None else "xb"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        quarantine_blocking(path)
        quarantine_stale_temp(tmp)
        with tmp.open(mode, encoding=encoding) as file:
            file.write(content)
            file.flush()
        fsync_content(tmp)
        if tmp.is_symlink():
            raise FileExistsError(f"{symlink_label} temp path became a symlink: {tmp}")
        tmp.replace(path)
        fsync_parent(path)
    except OSError:
        remove_temp(tmp)
        raise


def _write_corrupt_bytes_atomic(path: Path, data: bytes) -> None:
    """Write a corrupt artifact without exposing partial fallback bytes."""

    tmp_path = path.with_name(f"{path.name}.tmp")
    _quarantine_stale_corrupt_temp(tmp_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tmp_path.open("xb") as file:
            file.write(data)
            _fsync_corrupt_handle(file)
        final_path = path
        try:
            tmp_path.replace(final_path)
        except OSError:
            if not (final_path.exists() or final_path.is_symlink()):
                raise
            final_path = _available_corrupt_path(path)
            os.replace(tmp_path, final_path)
        _fsync_parent(final_path)
    except OSError:
        _remove_path_and_fsync_parent(tmp_path)
        raise


def _quarantine_stale_corrupt_temp(tmp_path: Path) -> None:
    """Preserve an interrupted fallback temp artifact before rewriting it."""

    if tmp_path.exists() or tmp_path.is_symlink():
        quarantine_corrupt_artifact(
            tmp_path,
            _stale_corrupt_temp_quarantine_path(tmp_path),
        )


def _stale_corrupt_temp_quarantine_path(tmp_path: Path) -> Path:
    """Return the quarantine path for an interrupted corrupt-artifact temp file."""

    return _available_corrupt_path(tmp_path.with_suffix(".corrupt"))


def corrupt_artifact_path_for(path: Path) -> Path:
    """Return the canonical ``.corrupt`` quarantine name for a state *path*.

    The vault, basket, and context-set stores each derived the same target name
    from these cases: a legacy ``{stem}.tmp.json`` temp (older writers staged
    temp state under this name) keeps its *full* name and gains a
    ``.corrupt.json`` suffix, so a non-file quarantine lands in the legacy
    temp's own corrupt family rather than collapsing onto the canonical ``.tmp``
    family (``context_sets.tmp.json`` -> ``context_sets.tmp.corrupt.json``) and
    stranding the artifact for a later run to trip over; an in-progress ``.tmp``
    temp keeps its full name and gains a ``.corrupt.json`` suffix (so a numbered
    collision stays in the temp's own family rather than colliding with the live
    state's), a ``.json`` payload swaps its extension for ``.corrupt.json``, and
    any other artifact gains a bare ``.corrupt`` suffix. The ``.tmp.json`` case
    is matched ahead of the ``.json`` case precisely so the ``.json``-strip does
    not collapse it. Sharing one definition keeps a blocking alias quarantined
    under the identical name regardless of which store handles it -- the basket
    and context-set stores previously kept their own copy of the ``.tmp.json``
    guard ahead of this delegation.
    """

    name = path.name
    if name.endswith(".tmp.json"):
        return path.with_name(f"{name}.corrupt.json")
    if name.endswith(".tmp"):
        return path.with_name(f"{name}.corrupt.json")
    if name.endswith(".json"):
        return path.with_name(f"{name[:-5]}.corrupt.json")
    return path.with_name(f"{name}.corrupt")


def _available_corrupt_path(corrupt_path: Path) -> Path:
    """Return the first deterministic quarantine path that is not in use."""

    if _corrupt_path_is_available(corrupt_path):
        return corrupt_path
    name = corrupt_path.name
    suffix = ".corrupt.json"
    if name.endswith(suffix):
        stem = name[: -len(suffix)]
        for index in range(1, _MAX_CORRUPT_PATH_CANDIDATES + 1):
            candidate = corrupt_path.with_name(f"{stem}.{index}{suffix}")
            if _corrupt_path_is_available(candidate):
                return candidate
        raise FileExistsError(f"no free corrupt artifact path for {corrupt_path}")
    for index in range(1, _MAX_CORRUPT_PATH_CANDIDATES + 1):
        candidate = corrupt_path.with_name(f"{name}.{index}")
        if _corrupt_path_is_available(candidate):
            return candidate
    raise FileExistsError(f"no free corrupt artifact path for {corrupt_path}")


def _corrupt_path_is_available(path: Path) -> bool:
    """Return true only when a corrupt artifact path can be safely created."""

    try:
        return not path.exists() and not path.is_symlink()
    except (OSError, RuntimeError):
        return False


def _corrupt_source_is_present(path: Path) -> bool:
    """Return true when a quarantine source should still be preserved."""

    try:
        return path.exists() or path.is_symlink()
    except (OSError, RuntimeError):
        # A failed probe should not discard a malformed local artifact before the
        # move/snapshot fallback has a chance to preserve it.
        return True


def remove_corrupt_artifact(path: Path) -> bool:
    """Remove a corrupt artifact file or directory without following symlinks."""

    try:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            os.remove(str(path))
        _fsync_parent(path)
        return True
    except Exception:
        return False


def clear_corrupt_artifact_family(corrupt_path: Path) -> int:
    """Remove primary and numbered corrupt artifacts for one logical state path."""

    if corrupt_path.name.endswith(".corrupt.json"):
        stem = corrupt_path.name[: -len(".corrupt.json")]
        candidates = (
            candidate
            for pattern in (
                corrupt_path.name,
                f"{stem}.*.corrupt.json",
                f"{stem}.stale.*.corrupt.json",
                f"{corrupt_path.name}.*",
            )
            for candidate in corrupt_path.parent.glob(pattern)
            if (
                candidate.name == corrupt_path.name
                or _has_numbered_corrupt_json_name(candidate.name, stem)
                or _has_stale_corrupt_json_name(candidate.name, stem)
                or _has_numbered_artifact_name(candidate.name, corrupt_path.name)
            )
        )
    else:
        candidates = (
            candidate
            for pattern in (corrupt_path.name, f"{corrupt_path.name}.*")
            for candidate in corrupt_path.parent.glob(pattern)
            if candidate.name == corrupt_path.name or _has_numbered_artifact_name(candidate.name, corrupt_path.name)
        )

    removed = 0
    seen: set[Path] = set()
    for candidate in sorted(candidates, key=lambda candidate: candidate.name):
        if candidate in seen:
            continue
        seen.add(candidate)
        if remove_corrupt_artifact(candidate):
            removed += 1
    return removed


def _is_ascii_decimal_index(index: str) -> bool:
    """Return ``True`` only for the ASCII-digit indices the emitter produces.

    ``_available_corrupt_path`` numbers collisions with ``f"{index}"`` over a
    ``range(1, _MAX_CORRUPT_PATH_CANDIDATES + 1)``, so every generated suffix is
    the canonical decimal spelling of a positive ``int``: plain ASCII ``[0-9]+``
    with no leading zero, starting at ``1``. ``str.isdecimal`` is broader on two
    axes. First, it accepts non-ASCII decimal digits such as Arabic-Indic (``١``)
    or fullwidth (``１``) forms. Second, even restricted to ASCII it accepts
    leading-zero or zero spellings (``01``, ``007``, ``0``) the emitter never
    writes. Either kind would let ``clear_corrupt_artifact_family`` treat an
    unrelated artifact like ``state.١.corrupt.json`` or ``state.01.corrupt.json``
    -- which this module never writes -- as a numbered family member and delete
    it. Restrict the match to the exact canonical indices actually emitted so
    clearing one logical state cannot remove a look-alike sibling that merely
    uses a foreign-digit or non-canonical index spelling.
    """

    if not (index and index.isascii() and index.isdecimal()):
        return False
    # ``isdecimal`` above guarantees ``int`` parses; require the canonical
    # positive-integer spelling the emitter actually produces (no leading zero,
    # ``>= 1``) so non-canonical look-alikes are left for manual inspection.
    return index == str(int(index)) and int(index) >= 1


def _has_numbered_corrupt_json_name(name: str, stem: str) -> bool:
    suffix = ".corrupt.json"
    if not name.startswith(f"{stem}.") or not name.endswith(suffix):
        return False
    index = name[len(stem) + 1 : -len(suffix)]
    return _is_ascii_decimal_index(index)


def _has_stale_corrupt_json_name(name: str, stem: str) -> bool:
    # A stale temp quarantine is written as ``{stem}.stale.corrupt.json`` and,
    # because that name ends in ``.corrupt.json``, ``_available_corrupt_path``
    # numbers collisions on the ``.corrupt.json`` stem -- i.e. as
    # ``{stem}.stale.{index}.corrupt.json``, not ``{stem}.stale.corrupt.json.{index}``.
    # Match the spelling the emitter actually produces so a numbered stale
    # collision is swept with the rest of its family instead of being stranded.
    stale_stem = f"{stem}.stale"
    return name == f"{stale_stem}.corrupt.json" or _has_numbered_corrupt_json_name(name, stale_stem)


def _has_numbered_artifact_name(name: str, base_name: str) -> bool:
    if not name.startswith(f"{base_name}."):
        return False
    index = name[len(base_name) + 1 :]
    return _is_ascii_decimal_index(index)


def quarantine_blocking_corrupt_artifact(path: Path) -> None:
    """Quarantine a non-file alias squatting where a store expects a JSON file.

    A symlink or non-file node (directory, FIFO, ...) sitting on a store's
    expected path would corrupt the next read, so move it aside under the shared
    corrupt-path family and let the store stage a fresh write. Plain files are
    left untouched -- those are payload-validation's concern, not this guard's.
    """

    if path.is_symlink() or (path.exists() and not path.is_file()):
        quarantine_corrupt_artifact(path, corrupt_artifact_path_for(path))


def quarantine_stale_corrupt_temp_artifact(path: Path) -> None:
    """Preserve a stale temp leftover before a store stages a fresh write.

    A plain-file leftover keeps its full ``{name}.stale.corrupt.json`` name so it
    lands in the temp's own corrupt family -- which the owning store's ``clear``
    sweeps -- instead of collapsing onto the canonical ``.tmp`` family that the
    shared namer would derive. A symlink or non-file alias has no such legacy
    family to preserve, so it routes through the shared namer directly.
    """

    if path.exists() or path.is_symlink():
        corrupt_path = (
            path.with_name(f"{path.name}.stale.corrupt.json")
            if path.is_file() and not path.is_symlink()
            else corrupt_artifact_path_for(path)
        )
        quarantine_corrupt_artifact(path, corrupt_path)


def quarantine_corrupt_artifact(path: Path, corrupt_path: Path) -> None:
    """Move *path* into *corrupt_path*, preserving directory snapshots if needed."""

    if path.name.endswith(".corrupt.json") or not _corrupt_source_is_present(path):
        return
    corrupt_path = _available_corrupt_path(corrupt_path)
    if corrupt_path.exists() or corrupt_path.is_symlink():
        corrupt_path = _available_corrupt_path(corrupt_path)
        if corrupt_path.exists() or corrupt_path.is_symlink():
            _remove_path_and_fsync_parent(path)
            return
    try:
        shutil.move(str(path), str(corrupt_path))
        _fsync_parent(corrupt_path)
        if path.parent != corrupt_path.parent:
            _fsync_parent(path)
        return
    except Exception:
        pass

    snapshot = snapshot_corrupt_artifact_bytes(path)
    if snapshot is not None:
        try:
            if is_directory_snapshot_bytes(snapshot):
                if restore_corrupt_artifact_bytes(corrupt_path, snapshot):
                    _remove_path_and_fsync_parent(path)
                    return
            else:
                corrupt_path.parent.mkdir(parents=True, exist_ok=True)
                _write_corrupt_bytes_atomic(corrupt_path, snapshot)
                _remove_path_and_fsync_parent(path)
                return
        except OSError:
            pass

    _remove_path_and_fsync_parent(path)
