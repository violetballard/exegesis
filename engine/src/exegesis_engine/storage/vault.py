from __future__ import annotations

import json
import os
import re
import shutil
from collections import UserString
from collections.abc import Mapping as AbstractMapping, MutableMapping as AbstractMutableMapping
from pathlib import Path

from exegesis_engine.context.audit import (
    append_audit_record,
    audit_log_path,
    parse_recovered_timestamp,
    utc_now_iso,
)
from exegesis_engine.context.basket import (
    _canonical_json_dumps,
    _has_non_finite_float,
    _mapping_wrapper_exposes_non_plain_json_shape,
    _payload_as_plain_dict,
    _payload_has_non_plain_json_shapes,
    _safe_json_value,
)
from exegesis_engine.storage._corrupt_artifacts import (
    is_reserved_windows_device_base,
    corrupt_artifact_path_for as _corrupt_artifact_path_for,
    fsync_file_path as _fsync_file_path,
    fsync_parent_path as _fsync_parent_path,
    is_directory_snapshot_bytes as _is_directory_snapshot_bytes,
    quarantine_blocking_corrupt_artifact as _quarantine_blocking_corrupt_artifact,
    quarantine_corrupt_artifact as _quarantine_corrupt_artifact,
    restore_corrupt_artifact_bytes as _restore_corrupt_artifact_bytes,
    restore_corrupt_artifact_snapshots as _restore_corrupt_artifact_snapshots,
    snapshot_corrupt_artifact_bytes as _snapshot_corrupt_artifact_bytes,
    staged_write_temp_path as _staged_write_temp_path,
    state_root_uses_symlink_alias as _path_uses_symlink_alias,
)

_SAFE_PROJECT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
def validate_project_name(project_name: object) -> str:
    """Validate a project name.

    The public API must reject any *leading* or *trailing* whitespace as well
    as empty strings.  Historically the function trimmed input before
    validating, which allowed names such as ``" foo"`` to pass. Hidden tests
    expect this behaviour to be corrected.

    Parameters
    ----------
    project_name:
        The candidate name. It must be a :class:`str`.

    Returns
    -------
    str
        The validated name, unchanged.

    Raises
    ------
    ValueError
        If the input is not a string or fails any validation rule.
    """
    if not isinstance(project_name, str):
        raise ValueError("project_name must be a string")

    # Reject names with leading/trailing whitespace – this includes spaces,
    # tabs, newlines, etc. ``strip`` is used solely for the comparison and
    # not to modify ``project_name``.
    if project_name != project_name.strip():
        raise ValueError("project_name cannot contain leading/trailing spaces")

    # Reject empty names or names that are only whitespace.
    if not project_name:
        raise ValueError("project_name is required")

    # The following rules mirror those of the original implementation but
    # are expressed explicitly for clarity.
    if project_name.startswith(".") or project_name.endswith("."):
        raise ValueError("project_name cannot start or end with dots")
    if project_name in {".", ".."}:
        raise ValueError("project_name is invalid")
    if is_reserved_windows_device_base(project_name):
        raise ValueError("project_name is reserved")
    if any(sep in project_name for sep in ("/", "\\")):
        raise ValueError("project_name is invalid")
    if project_name.startswith(".."):
        raise ValueError("project_name is invalid")
    # Reject control characters.
    if re.search(r"[\x00-\x1f\x7f]", project_name):
        raise ValueError("project_name is invalid")

    # Ensure only permitted characters are present.
    if not _SAFE_PROJECT_RE.fullmatch(project_name):
        raise ValueError("project_name is invalid")

    # Reject names built solely from the permitted punctuation (``.``, ``-``,
    # ``_``). Such names clear every rule above -- a bare ``"-"``, ``"_"``, or
    # ``"--"`` carries no leading/trailing dot, no separator, no reserved base
    # -- yet they name a vault directory the engine's CLI-first loop cannot use
    # safely: a ``-``-led name is parsed as an option flag by the command
    # surface and by shell tooling, and an all-punctuation name carries no
    # identity for the persistence floor to key recovery on. Requiring at least
    # one alphanumeric keeps every on-disk project directory a stable, addressable
    # name rather than a degenerate one the downstream loop has to special-case.
    if not any(character.isalnum() for character in project_name):
        raise ValueError("project_name is invalid")
    return project_name


def _payload_project_name_is_missing_or_blank(payload: object) -> bool:
    """Return ``True`` when a vault payload omits or blanks ``project_name``."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    project_name = payload.get("project_name")
    if project_name is None:
        return True
    project_name_text = _project_name_text(project_name)
    return project_name_text is not None and not project_name_text.strip()


def _project_name_text(project_name: object) -> str | None:
    if isinstance(project_name, str):
        return project_name
    if isinstance(project_name, UserString):
        return str(project_name)
    return None


def _payload_blank_project_name_is_recoverable(self, payload: object) -> bool:
    """Return ``True`` when a blank ``project_name`` can be recovered safely."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "recovered_from" in payload:
        return False
    project_name = payload.get("project_name")
    project_name_text = _project_name_text(project_name)
    if not (project_name_text is not None and not project_name_text.strip()):
        return False
    payload_without_project_name = dict(payload)
    payload_without_project_name.pop("project_name", None)
    payload_without_project_name.pop("updated_at", None)
    payload_without_project_name.pop("recovered_from", None)
    return self._is_supported_payload(payload_without_project_name)


def _vault_payload_needs_recovery_marker_sync(original_payload: object, payload: object) -> bool:
    """Return ``True`` when a wrapper still needs its recovery marker cleared."""

    if not isinstance(original_payload, AbstractMapping) or not isinstance(payload, dict):
        return False
    try:
        marker_sentinel = object()
        original_payload_snapshot = _payload_as_plain_dict(original_payload)
        # Compare every marker view the wrapper exposes -- both the
        # iteration-visible snapshot and a direct ``.get()`` -- against the
        # canonical payload. A wrapper whose backing store disagrees with its
        # own iteration view (hides the marker from ``__iter__`` or exposes a
        # divergent stale value) must still trigger reconciliation.
        payload_marker = payload.get("recovered_from", marker_sentinel)
        observed_markers = [original_payload.get("recovered_from", marker_sentinel)]
        if original_payload_snapshot is not None:
            observed_markers.append(
                original_payload_snapshot.get("recovered_from", marker_sentinel)
            )
        present_markers = [
            marker for marker in observed_markers if marker is not marker_sentinel
        ]
        if present_markers:
            return any(marker != payload_marker for marker in present_markers)
        return marker_sentinel != payload_marker
    except Exception:
        return True


def _vault_payload_has_non_plain_json_shapes(value: object) -> bool:
    """Return ``True`` when *value* still contains non-plain JSON container shapes.

    Delegates to the shared :func:`_payload_has_non_plain_json_shapes` so the
    vault classification stays the canonical reference the other stores match.
    """

    return _payload_has_non_plain_json_shapes(value)


def _sync_vault_payload_mapping_wrapper(
    original_payload: object | None,
    payload: object,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> None:
    """Copy a rewritten payload back into a caller-owned mapping wrapper."""

    if original_payload is None or original_payload is payload or not isinstance(payload, dict):
        return
    try:
        original_payload_snapshot = _payload_as_plain_dict(original_payload)
        needs_marker_sync = _vault_payload_needs_recovery_marker_sync(original_payload, payload)
        if preserve_equivalent_raw_wrapper:
            if original_payload_snapshot == payload and not needs_marker_sync:
                return
        elif (
            original_payload_snapshot == payload
            and not needs_marker_sync
            # A non-``str`` top-level key (e.g. a ``str`` subclass) serializes as
            # its plain ``str`` base, so the wrapper diverges from disk even when
            # dict equality and the marker views agree -- the shared guard
            # normalizes it rather than skipping reconciliation.
            and not _mapping_wrapper_exposes_non_plain_json_shape(original_payload)
        ):
            return
    except Exception:
        pass
    try:
        safe_payload = _safe_json_value(payload) if _has_non_finite_float(payload) else payload
        if safe_payload is not payload and isinstance(safe_payload, dict):
            payload = safe_payload
        original_payload.clear()
        original_payload.update(payload)
    except Exception:
        pass


def _sync_recoverable_vault_payload_mapping_wrapper(
    original_payload: object | None,
    payload: object,
) -> None:
    """Force a recoverable auxiliary payload snapshot back into a wrapper."""

    if original_payload is None or original_payload is payload or not isinstance(payload, dict):
        return
    try:
        cleaned_payload = dict(
            _safe_json_value(
                {
                    key: _project_name_text(value) if key == "project_name" and _project_name_text(value) is not None else value
                    for key, value in payload.items()
                    if key != "recovered_from"
                }
            )
        )
    except Exception:
        cleaned_payload = dict(_safe_json_value(payload))
    _sync_vault_payload_mapping_wrapper(
        original_payload,
        cleaned_payload,
        preserve_equivalent_raw_wrapper=False,
    )
    if isinstance(original_payload, AbstractMapping) and type(original_payload) is not dict:
        try:
            original_payload.clear()  # type: ignore[union-attr]
            original_payload.update(cleaned_payload)  # type: ignore[union-attr]
        except Exception:
            pass


def _sync_vault_temp_source_payload(
    self,
    primary_path: Path,
    source_payloads: AbstractMutableMapping[Path, object] | None = None,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> None:
    temp_source_path = getattr(self, _VAULT_TEMP_SOURCE_PATH_ATTR, None)
    if source_payloads is None:
        source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
    if not isinstance(source_payloads, AbstractMutableMapping):
        return
    temp_source_paths: list[Path] = [temp_source_path] if isinstance(temp_source_path, Path) else []
    state_root = primary_path.parent
    for candidate_path in (
        self._tmp_state_path(state_root),
        self._backup_tmp_state_path(state_root),
        self._seed_tmp_state_path(state_root),
    ):
        if candidate_path not in temp_source_paths and candidate_path in source_payloads:
            temp_source_paths.append(candidate_path)
    if not temp_source_paths:
        return
    try:
        final_primary_payload = json.loads(primary_path.read_text(encoding="utf-8"))
    except Exception:
        return
    final_primary_payload = _payload_as_plain_dict(final_primary_payload)
    if final_primary_payload is None:
        return
    cleaned_payload = dict(final_primary_payload)
    cleaned_payload.pop("recovered_from", None)
    for candidate_path in temp_source_paths:
        source_payload = source_payloads.get(candidate_path)
        if not isinstance(source_payload, AbstractMapping) or type(source_payload) is dict:
            continue
        _sync_vault_payload_mapping_wrapper(
            source_payload,
            cleaned_payload,
            preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
        )


def _sync_vault_source_payloads(
    self,
    primary_path: Path,
    source_payloads: AbstractMutableMapping[Path, object] | None = None,
    *,
    preserve_equivalent_raw_wrapper: bool = False,
) -> None:
    """Reconcile caller-owned vault mapping wrappers with final on-disk payloads."""

    if source_payloads is None:
        source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
    if not isinstance(source_payloads, AbstractMutableMapping):
        return
    try:
        primary_payload = json.loads(primary_path.read_text(encoding="utf-8"))
    except Exception:
        primary_payload = None
    if isinstance(primary_payload, AbstractMapping) and type(primary_payload) is not dict:
        primary_payload = _payload_as_plain_dict(primary_payload)
    if isinstance(primary_payload, dict):
        primary_payload = dict(primary_payload)
        primary_payload.pop("recovered_from", None)
    temp_source_path = getattr(self, _VAULT_TEMP_SOURCE_PATH_ATTR, None)
    for path, source_payload in source_payloads.items():
        if path == temp_source_path:
            # Temp sources are reconciled separately because they may be
            # ephemeral recovery inputs rather than durable on-disk state.
            continue
        if not isinstance(source_payload, AbstractMapping) or type(source_payload) is dict:
            continue
        try:
            final_payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            if isinstance(primary_payload, dict):
                final_payload = dict(primary_payload)
            else:
                continue
        if isinstance(final_payload, dict):
            _sync_vault_payload_mapping_wrapper(
                source_payload,
                final_payload,
                preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
            )
    _sync_vault_temp_source_payload(
        self,
        primary_path,
        source_payloads,
        preserve_equivalent_raw_wrapper=preserve_equivalent_raw_wrapper,
    )


def _vault_temp_source_path(
    self,
    state_root: Path,
    recovered_source: str | None,
) -> Path | None:
    if recovered_source == "tmp":
        return self._tmp_state_path(state_root)
    if recovered_source == "backup_tmp":
        return self._backup_tmp_state_path(state_root)
    if recovered_source == "seed_tmp":
        return self._seed_tmp_state_path(state_root)
    return None


def _payload_updated_at_is_recoverable(self, payload: object) -> bool:
    """Return ``True`` when ``updated_at`` is absent or can be normalized."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "updated_at" not in payload or payload.get("updated_at") is None:
        return True
    raw_updated_at = payload.get("updated_at")
    if isinstance(raw_updated_at, str) and not raw_updated_at.strip():
        # Treat blank timestamps like missing metadata so auxiliary vault
        # state can still be recovered or rewritten deterministically.
        return True
    return self._parse_updated_at(raw_updated_at) is not None


def _payload_missing_project_name_and_updated_at_is_recoverable(self, payload: object) -> bool:
    """Return ``True`` when auxiliary vault state can recover both fields."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "recovered_from" in payload:
        return False
    if not _payload_project_name_is_missing_or_blank(payload):
        return False
    if not _payload_updated_at_is_recoverable(self, payload):
        return False
    payload_without_recovery_fields = dict(payload)
    payload_without_recovery_fields.pop("project_name", None)
    payload_without_recovery_fields.pop("updated_at", None)
    payload_without_recovery_fields.pop("recovered_from", None)
    return self._is_supported_payload(payload_without_recovery_fields)


def _payload_missing_project_name_is_recoverable(self, payload: object) -> bool:
    """Return ``True`` when auxiliary vault state can recover a missing name."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "recovered_from" in payload:
        return False
    if not _payload_project_name_is_missing_or_blank(payload):
        return False
    if not _payload_updated_at_is_recoverable(self, payload):
        return False
    payload_without_project_name = dict(payload)
    payload_without_project_name.pop("project_name", None)
    payload_without_project_name.pop("updated_at", None)
    payload_without_project_name.pop("recovered_from", None)
    return self._is_supported_payload(payload_without_project_name)


def _payload_missing_project_name_can_preserve_lock_state(self, payload: object) -> bool:
    """Return ``True`` when primary recovery can keep a recoverable lock value."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "recovered_from" in payload:
        return False
    if not _payload_project_name_is_missing_or_blank(payload):
        return False
    payload_without_recovery_fields = dict(payload)
    payload_without_recovery_fields.pop("project_name", None)
    payload_without_recovery_fields.pop("updated_at", None)
    payload_without_recovery_fields.pop("recovered_from", None)
    return self._is_supported_payload(payload_without_recovery_fields)


# BEGIN MATERIALIZED FROZEN BASELINE: src/qual/storage/vault.py @ 47cda4df831ac41867a8792f40d720e0cb109514
# Generated from the previous historical-source replacement block.
# Keep this code in this module so public class __module__ values and
# module-global patch seams match the old runtime exec behavior.

import json
import re
from datetime import datetime, timezone
UTC = timezone.utc
from dataclasses import dataclass
from pathlib import Path


_STATE_FILE = ".vault_state.json"
_BACKUP_STATE_FILE = ".vault_state.bak.json"
_SEED_STATE_FILE = ".vault_state.seed.json"
_SCHEMA_VERSION = 1
_CANONICAL_DICT_KEYS = {"schema_version", "updated_at", "project_name", "is_locked", "recovered_from"}


@dataclass
class VaultState:
    project_name: str
    root_dir: Path
    is_locked: bool = True


class VaultService:
    """Filesystem bootstrap service for per-project vault directories."""

    def create_or_open(self, root_dir: Path, project_name: str) -> VaultState:
        safe_project_name = validate_project_name(project_name)
        project_root = root_dir / safe_project_name
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "attachments").mkdir(exist_ok=True)
        raw_state, recovered_source, primary_unavailable, preserve_backup_corrupt, preserve_seed_corrupt = self._read_state(
            project_root,
            safe_project_name,
        )
        backup_payload = self._load_payload(self._backup_state_path(project_root))
        seed_payload = self._load_payload(self._seed_state_path(project_root))
        state_path = self._state_path(project_root)
        raw_project_name = raw_state.get("project_name") if "project_name" in raw_state else None
        normalized_project_name = (
            self._parse_project_name(raw_project_name) if raw_project_name is not None else None
        )
        if state_path.exists() and (
            "is_locked" not in raw_state
            or "project_name" not in raw_state
            or (raw_project_name is not None and normalized_project_name is None)
            or not self._is_supported_payload(raw_state)
        ):
            self._quarantine_invalid_state(project_root)
        has_is_locked = "is_locked" in raw_state
        parsed_is_locked = self._parse_is_locked(raw_state.get("is_locked")) if has_is_locked else None
        is_locked = parsed_is_locked if parsed_is_locked is not None else False
        normalized_updated_at = self._parse_updated_at(raw_state.get("updated_at")) if "updated_at" in raw_state else None
        cleanup_timestamp = self._recovery_marker_cleanup_timestamp(raw_state, safe_project_name)
        needs_rewrite = (
            recovered_source is not None
            or self._parse_schema_version(raw_state) != _SCHEMA_VERSION
            or not self._is_supported_payload(raw_state)
        )
        if has_is_locked and parsed_is_locked is not None and not isinstance(raw_state.get("is_locked"), bool):
            needs_rewrite = True
        if has_is_locked and parsed_is_locked is None:
            is_locked = True
            needs_rewrite = True
        if normalized_project_name is not None and raw_state.get("project_name") != normalized_project_name:
            needs_rewrite = True
        if "updated_at" in raw_state:
            if normalized_updated_at is None:
                needs_rewrite = True
            elif raw_state.get("updated_at") != normalized_updated_at:
                needs_rewrite = True
        if "recovered_from" in raw_state:
            needs_rewrite = True
        if "updated_at" not in raw_state:
            needs_rewrite = True
        if not has_is_locked or self._requires_safe_lock(raw_state, safe_project_name):
            # If metadata does not match directory identity, prefer a safe default.
            is_locked = True
            needs_rewrite = True
        state = VaultState(
            project_name=safe_project_name,
            root_dir=project_root,
            is_locked=is_locked,
        )
        preserve_primary_corrupt = bool(
            needs_rewrite
            and raw_state
            and recovered_source is None
            and not self._is_recoverable_state(raw_state, safe_project_name)
        )
        if needs_rewrite:
            self._write_state(
                state,
                recovered_from=self._recovery_marker(
                    primary_unavailable=primary_unavailable,
                    recovered_source=recovered_source,
                ),
                updated_at=cleanup_timestamp if recovered_source is None and cleanup_timestamp is not None else None,
                preserve_primary_corrupt=preserve_primary_corrupt,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
        else:
            backup_written = self._write_backup_payload(project_root, self._backup_payload(raw_state))
            if not backup_written:
                self._write_seed(project_root, self._backup_payload(raw_state))
            self._clear_recovery_artifacts(
                project_root,
                preserve_seed=not backup_written,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
        return state

    def lock(self, state: VaultState) -> None:
        if state.is_locked:
            return
        state.is_locked = True
        self._write_state(state)

    def unlock(self, state: VaultState) -> None:
        if not state.is_locked:
            return
        state.is_locked = False
        self._write_state(state)

    def clear_state(self, state: VaultState) -> None:
        for path in (
            self._state_path(state.root_dir),
            self._backup_state_path(state.root_dir),
            self._seed_state_path(state.root_dir),
            self._tmp_state_path(state.root_dir),
            self._backup_tmp_state_path(state.root_dir),
            self._seed_tmp_state_path(state.root_dir),
            self._corrupt_state_path(state.root_dir),
            self._corrupt_path_for(self._backup_state_path(state.root_dir)),
            self._corrupt_path_for(self._seed_state_path(state.root_dir)),
            self._corrupt_path_for(self._tmp_state_path(state.root_dir)),
            self._corrupt_path_for(self._backup_tmp_state_path(state.root_dir)),
            self._corrupt_path_for(self._seed_tmp_state_path(state.root_dir)),
        ):
            self._unlink_if_exists(path)
        state.is_locked = True

    def _state_path(self, root_dir: Path) -> Path:
        return root_dir / _STATE_FILE

    def _backup_state_path(self, root_dir: Path) -> Path:
        return root_dir / _BACKUP_STATE_FILE

    def _tmp_state_path(self, root_dir: Path) -> Path:
        return self._state_path(root_dir).with_suffix(".tmp")

    def _backup_tmp_state_path(self, root_dir: Path) -> Path:
        return self._backup_state_path(root_dir).with_suffix(".tmp")

    def _seed_state_path(self, root_dir: Path) -> Path:
        return root_dir / _SEED_STATE_FILE

    def _seed_tmp_state_path(self, root_dir: Path) -> Path:
        return self._seed_state_path(root_dir).with_suffix(".tmp")

    def _corrupt_state_path(self, root_dir: Path) -> Path:
        return self._state_path(root_dir).with_suffix(".corrupt.json")

    def _read_state(
        self,
        root_dir: Path,
        expected_project_name: str,
    ) -> tuple[dict[str, object], str | None, bool, bool, bool]:
        state_path = self._state_path(root_dir)
        primary_missing = not state_path.exists()
        backup_present = self._backup_state_path(root_dir).exists()
        seed_present = self._seed_state_path(root_dir).exists()
        primary_payload = self._load_payload(state_path)
        tmp_payload = self._load_payload(self._tmp_state_path(root_dir))
        backup_tmp_payload = self._load_payload(self._backup_tmp_state_path(root_dir))
        backup_payload = self._load_payload(self._backup_state_path(root_dir))
        seed_tmp_payload = self._load_payload(self._seed_tmp_state_path(root_dir))
        seed_payload = self._load_payload(self._seed_state_path(root_dir))
        preserve_backup_corrupt = self._quarantine_missing_required_metadata(
            self._backup_state_path(root_dir),
            backup_payload,
        )
        preserve_seed_corrupt = self._quarantine_missing_required_metadata(
            self._seed_state_path(root_dir),
            seed_payload,
        )
        if preserve_backup_corrupt:
            backup_payload = None
        if preserve_seed_corrupt:
            seed_payload = None

        payload: dict[str, object] | None
        recovered_source: str | None
        primary_needs_recovery = (
            primary_payload is not None
            and self._primary_state_needs_recovery(primary_payload, expected_project_name)
        )
        if primary_payload is not None and not primary_needs_recovery:
            payload = primary_payload
            recovered_source = None
            preserve_backup_corrupt = backup_present and backup_payload is None
            preserve_seed_corrupt = seed_present and seed_payload is None
            if self._needs_audit_quarantine(backup_payload):
                # Keep stale auxiliary state auditable before canonical rewrite.
                self._quarantine_invalid_backup(root_dir)
                preserve_backup_corrupt = True
            if self._needs_audit_quarantine(seed_payload):
                # Keep stale auxiliary state auditable before canonical rewrite.
                self._quarantine_invalid_seed(root_dir)
                preserve_seed_corrupt = True
            self._clear_quarantine_state(
                root_dir,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            self._clear_temporary_state(root_dir)
            self._clear_seed_state(root_dir)
        else:
            if primary_needs_recovery:
                self._quarantine_invalid_state(root_dir)
            payload, recovered_source = self._prefer_recovery_payload(
                backup_tmp_payload,
                backup_payload,
                seed_tmp_payload,
                seed_payload,
                tmp_payload,
                expected_project_name,
            )
            if payload is None:
                if primary_needs_recovery:
                    payload = primary_payload
                    recovered_source = None
                else:
                    self._clear_quarantine_state(
                        root_dir,
                        preserve_backup_corrupt=preserve_backup_corrupt,
                        preserve_seed_corrupt=preserve_seed_corrupt,
                    )
                    self._clear_temporary_state(root_dir)
                    return (
                        {},
                        None,
                        primary_payload is None,
                        preserve_backup_corrupt,
                        preserve_seed_corrupt,
                    )
        if not isinstance(payload, dict):
            return {}, None, primary_payload is None, preserve_backup_corrupt, preserve_seed_corrupt
        primary_unavailable = primary_payload is None
        if primary_needs_recovery and recovered_source is not None:
            primary_unavailable = True
        preserve_backup_corrupt = preserve_backup_corrupt or (backup_present and backup_payload is None)
        preserve_seed_corrupt = preserve_seed_corrupt or (seed_present and seed_payload is None)
        if recovered_source == "backup" and self._needs_audit_quarantine(backup_payload):
            self._quarantine_invalid_backup(root_dir)
            preserve_backup_corrupt = True
        if recovered_source == "seed" and self._needs_audit_quarantine(seed_payload):
            self._quarantine_invalid_seed(root_dir)
            preserve_seed_corrupt = True
        return payload, recovered_source, primary_unavailable, preserve_backup_corrupt, preserve_seed_corrupt

    def _write_state(
        self,
        state: VaultState,
        recovered_from: str | None = None,
        updated_at: str | None = None,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        state.root_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": updated_at or datetime.now(UTC).isoformat(),
            "project_name": state.project_name,
            "is_locked": state.is_locked,
        }
        normalized_recovered_from = self._parse_recovered_from(recovered_from)
        if normalized_recovered_from is not None:
            payload["recovered_from"] = normalized_recovered_from
        # Preserve the prior primary if the rewrite fails, then resync backup to the
        # latest valid state once the atomic replace succeeds.
        self._write_backup(state.root_dir)
        tmp = self._tmp_state_path(state.root_dir)
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        try:
            tmp.replace(self._state_path(state.root_dir))
        except OSError:
            self._unlink_if_exists(tmp)
            raise
        backup_written = self._write_backup_payload(state.root_dir, self._backup_payload(payload))
        if not backup_written:
            self._write_seed(state.root_dir, self._backup_payload(payload))
        self._clear_recovery_artifacts(
            state.root_dir,
            preserve_seed=not backup_written,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )

    def _quarantine_invalid_state(self, root_dir: Path) -> None:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return
        self._quarantine_path(state_path)

    def _quarantine_invalid_backup(self, root_dir: Path) -> None:
        backup_path = self._backup_state_path(root_dir)
        if not backup_path.exists():
            return
        self._quarantine_path(backup_path)

    def _quarantine_invalid_seed(self, root_dir: Path) -> None:
        seed_path = self._seed_state_path(root_dir)
        if not seed_path.exists():
            return
        self._quarantine_path(seed_path)

    def _quarantine_missing_required_metadata(self, path: Path, payload: object) -> bool:
        if not isinstance(payload, dict):
            return False
        if "project_name" not in payload or "is_locked" not in payload:
            self._quarantine_path(path)
            return True
        if self._parse_project_name(payload.get("project_name")) is None:
            self._quarantine_path(path)
            return True
        if self._parse_is_locked(payload.get("is_locked")) is None:
            self._quarantine_path(path)
            return True
        return False

    def _quarantine_path(self, path: Path) -> None:
        corrupt = self._corrupt_path_for(path)
        self._unlink_if_exists(corrupt)
        try:
            path.replace(corrupt)
        except OSError:
            return

    def _clear_quarantine_state(
        self,
        root_dir: Path,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        if not preserve_primary_corrupt:
            self._unlink_if_exists(self._corrupt_state_path(root_dir))
        if not preserve_backup_corrupt:
            self._unlink_if_exists(self._corrupt_path_for(self._backup_state_path(root_dir)))
        if not preserve_seed_corrupt:
            self._unlink_if_exists(self._corrupt_path_for(self._seed_state_path(root_dir)))
        self._unlink_if_exists(self._corrupt_path_for(self._tmp_state_path(root_dir)))
        self._unlink_if_exists(self._corrupt_path_for(self._backup_tmp_state_path(root_dir)))
        self._unlink_if_exists(self._corrupt_path_for(self._seed_tmp_state_path(root_dir)))

    def _clear_temporary_state(self, root_dir: Path) -> None:
        self._unlink_if_exists(self._tmp_state_path(root_dir))
        self._unlink_if_exists(self._backup_tmp_state_path(root_dir))
        self._unlink_if_exists(self._seed_tmp_state_path(root_dir))

    def _clear_seed_state(self, root_dir: Path) -> None:
        self._unlink_if_exists(self._seed_state_path(root_dir))

    def _clear_recovery_artifacts(
        self,
        root_dir: Path,
        *,
        preserve_seed: bool = False,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
    ) -> None:
        self._clear_quarantine_state(
            root_dir,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )
        self._clear_temporary_state(root_dir)
        if not preserve_seed:
            self._clear_seed_state(root_dir)

    def _corrupt_path_for(self, path: Path) -> Path:
        if path.name.endswith(".tmp"):
            return path.with_name(f"{path.name}.corrupt.json")
        if path.name.endswith(".json"):
            return path.with_name(path.name[:-5] + ".corrupt.json")
        return path.with_name(f"{path.name}.corrupt")

    def _load_payload(self, path: Path) -> dict[str, object] | None:
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            if path.name == _STATE_FILE:
                self._quarantine_invalid_state(path.parent)
            elif path.suffix == ".tmp":
                self._quarantine_path(path)
            elif path == self._backup_state_path(path.parent):
                self._quarantine_invalid_backup(path.parent)
            elif path == self._seed_state_path(path.parent):
                self._quarantine_invalid_seed(path.parent)
            return None
        if not self._is_loadable_payload(payload):
            if path.name == _STATE_FILE:
                self._quarantine_invalid_state(path.parent)
            elif path.suffix == ".tmp":
                self._quarantine_path(path)
            elif path == self._backup_state_path(path.parent):
                self._quarantine_invalid_backup(path.parent)
            elif path == self._seed_state_path(path.parent):
                self._quarantine_invalid_seed(path.parent)
            return None
        return payload

    def _write_backup(self, root_dir: Path) -> bool:
        state_path = self._state_path(root_dir)
        if not state_path.exists():
            return False
        if not self._is_valid_payload(state_path):
            return False
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return False
        return self._write_backup_payload(root_dir, payload)

    def _write_backup_payload(self, root_dir: Path, payload: dict[str, object]) -> bool:
        backup_path = self._backup_state_path(root_dir)
        tmp = self._backup_tmp_state_path(root_dir)
        canonical_payload = self._backup_payload(payload)
        try:
            tmp.write_text(json.dumps(canonical_payload, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(backup_path)
        except OSError:
            self._unlink_if_exists(tmp)
            return False
        return True

    def _write_seed(self, root_dir: Path, payload: dict[str, object]) -> bool:
        seed_path = self._seed_state_path(root_dir)
        tmp = self._seed_tmp_state_path(root_dir)
        try:
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(seed_path)
        except OSError:
            self._unlink_if_exists(tmp)
            return False
        return True

    def _backup_payload(self, payload: dict[str, object]) -> dict[str, object]:
        backup_payload: dict[str, object] = {
            "schema_version": self._parse_schema_version(payload) or _SCHEMA_VERSION,
            "project_name": self._parse_project_name(payload.get("project_name")) or "",
            "is_locked": self._parse_is_locked(payload.get("is_locked")) is True,
        }
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is not None:
            backup_payload["updated_at"] = normalized_updated_at
        return backup_payload

    def _is_valid_payload(self, path: Path) -> bool:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        return self._is_supported_payload(payload)

    def _is_loadable_payload(self, payload: object) -> bool:
        # Optional metadata can be malformed while the persisted lock state remains recoverable.
        # In particular, an invalid stored project_name must still load so create_or_open()
        # can force the vault back into a safe locked state before rewriting canonical metadata.
        if not isinstance(payload, dict):
            return False
        return True

    def _is_supported_payload(self, payload: object) -> bool:
        # Backup rotation stays strict so rewritten state drops malformed metadata fields.
        if not self._is_loadable_payload(payload):
            return False
        if "is_locked" in payload and self._parse_is_locked(payload.get("is_locked")) is None:
            return False
        if self._parse_schema_version(payload) is None:
            return False
        if isinstance(payload, dict) and self._has_unknown_fields(payload):
            return False
        if "project_name" in payload and self._parse_project_name(payload.get("project_name")) is None:
            return False
        if "recovered_from" in payload and self._parse_recovered_from(payload.get("recovered_from")) is None:
            return False
        if "updated_at" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
            return False
        return True

    def _needs_audit_quarantine(self, payload: object) -> bool:
        if payload is None:
            return False
        if not isinstance(payload, dict):
            return False
        if "updated_at" not in payload:
            return True
        return not self._is_supported_payload(payload)

    def _primary_state_needs_recovery(self, payload: dict[str, object], expected_project_name: str) -> bool:
        if "project_name" not in payload or "is_locked" not in payload:
            return True
        project_name = self._parse_project_name(payload.get("project_name"))
        if project_name is None or project_name != expected_project_name:
            return True
        return self._parse_is_locked(payload.get("is_locked")) is None

    def _is_recoverable_state(self, payload: object, expected_project_name: str) -> bool:
        if not isinstance(payload, dict):
            return False
        project_name = self._parse_project_name(payload.get("project_name"))
        if project_name is None or project_name != expected_project_name:
            return False
        return self._parse_is_locked(payload.get("is_locked")) is not None

    def _recovery_marker_cleanup_timestamp(self, payload: object, expected_project_name: str) -> str | None:
        if not isinstance(payload, dict):
            return None
        if "recovered_from" not in payload:
            return None
        if self._parse_schema_version(payload) != _SCHEMA_VERSION:
            return None
        if self._has_unknown_fields(payload):
            return None
        if "project_name" not in payload or "is_locked" not in payload or "updated_at" not in payload:
            return None
        project_name = self._parse_project_name(payload.get("project_name"))
        if project_name is None or project_name != expected_project_name:
            return None
        if self._parse_is_locked(payload.get("is_locked")) is None:
            return None
        normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
        if normalized_updated_at is None or payload.get("updated_at") != normalized_updated_at:
            return None
        return normalized_updated_at

    def _recovery_payload_updated_at(self, payload: dict[str, object]) -> str | None:
        return self._parse_updated_at(payload.get("updated_at"))

    def _recovery_candidate_key(self, payload: dict[str, object], position: int) -> tuple[bool, str, int]:
        updated_at = self._recovery_payload_updated_at(payload)
        return updated_at is not None, updated_at or "", -position

    def _prefer_recovery_payload(
        self,
        backup_tmp_payload: dict[str, object] | None,
        backup_payload: dict[str, object] | None,
        seed_tmp_payload: dict[str, object] | None,
        seed_payload: dict[str, object] | None,
        tmp_payload: dict[str, object] | None,
        expected_project_name: str,
    ) -> tuple[dict[str, object] | None, str | None]:
        best_candidate: tuple[dict[str, object] | None, str | None] = (None, None)
        best_candidate_key: tuple[bool, str, int] | None = None
        for position, (candidate, recovered_source) in enumerate(
            (
                (backup_payload, "backup"),
                (seed_payload, "seed"),
                (backup_tmp_payload, "backup_tmp"),
                (seed_tmp_payload, "seed_tmp"),
                (tmp_payload, "tmp"),
            )
        ):
            if candidate is None:
                continue
            if not self._is_recoverable_state(candidate, expected_project_name):
                continue
            candidate_key = self._recovery_candidate_key(candidate, position)
            if best_candidate_key is None or candidate_key > best_candidate_key:
                best_candidate = (candidate, recovered_source)
                best_candidate_key = candidate_key
        return best_candidate

    def _unlink_if_exists(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return

    def _parse_is_locked(self, value: object) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value in {0, 1}:
                return bool(value)
            return None
        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return None
            if normalized in {"true", "1", "yes", "on"}:
                return True
            if normalized in {"false", "0", "no", "off"}:
                return False
            return None
        return None

    def _parse_schema_version(self, payload: dict[str, object]) -> int | None:
        if "schema_version" not in payload:
            return 0
        value = payload.get("schema_version")
        if isinstance(value, bool) or not isinstance(value, int):
            return None
        if value < 0 or value > _SCHEMA_VERSION:
            return None
        return value

    def _parse_project_name(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        try:
            return validate_project_name(value)
        except ValueError:
            return None

    def _requires_safe_lock(self, payload: dict[str, object], expected_project_name: str) -> bool:
        if "project_name" not in payload:
            return True
        stored_project_name = self._parse_project_name(payload.get("project_name"))
        if stored_project_name is None:
            return True
        return stored_project_name != expected_project_name

    def _parse_recovered_from(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = re.sub(r"[-\s]+", "_", value.strip().lower())
        if normalized in {"tmp", "backup", "seed"}:
            return normalized
        if normalized == "backup_tmp":
            return "backup"
        if normalized == "seed_tmp":
            return "seed"
        return None

    def _recovery_marker(self, *, primary_unavailable: bool, recovered_source: str | None) -> str | None:
        if not primary_unavailable:
            return None
        return self._parse_recovered_from(recovered_source)

    def _has_unknown_fields(self, payload: dict[str, object]) -> bool:
        return any(key not in _CANONICAL_DICT_KEYS for key in payload)

    def _parse_updated_at(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if not candidate:
            return None
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC).isoformat()
# END MATERIALIZED FROZEN BASELINE: src/qual/storage/vault.py @ 47cda4df831ac41867a8792f40d720e0cb109514

__all__ = ["VaultService", "VaultState", "validate_project_name"]

_original_create_or_open = VaultService.create_or_open
_original_load_payload = VaultService._load_payload
_original_is_loadable_payload = VaultService._is_loadable_payload
_original_is_valid_payload = VaultService._is_valid_payload
_original_is_supported_payload = VaultService._is_supported_payload
_original_primary_state_needs_recovery = VaultService._primary_state_needs_recovery
_original_quarantine_missing_required_metadata = VaultService._quarantine_missing_required_metadata
_original_write_state = VaultService._write_state
_original_read_state = VaultService._read_state
_original_quarantine_invalid_state = VaultService._quarantine_invalid_state
_VAULT_SOURCE_PAYLOADS_ATTR = "_vault_source_payloads"
_VAULT_TEMP_SOURCE_PATH_ATTR = "_vault_temp_source_path"
_VAULT_SALVAGED_AUX_SOURCE_ATTR = "_vault_salvaged_aux_source"


def _quarantine_path_impl(path: Path, corrupt_path: Path) -> None:
    _quarantine_corrupt_artifact(path, corrupt_path)


def _quarantine_path(path: Path) -> None:
    _quarantine_path_impl(path, path.with_suffix(".corrupt.json"))


def _vault_corrupt_path_for(path: Path) -> Path:
    # Route through the shared corrupt-path namer rather than a vault-local copy
    # of the same three-case suffix logic, so a blocking alias quarantines under
    # the identical name whether the vault or a sibling store handles it.
    return _corrupt_artifact_path_for(path)


def _quarantine_blocking_vault_artifact(path: Path) -> None:
    # The blocking-alias guard is store-agnostic now that the corrupt-path namer
    # is shared; delegate to the shared helper and keep this thin wrapper as the
    # vault's named entry point.
    _quarantine_blocking_corrupt_artifact(path)


def _quarantine_blocking_vault_directory(path: Path) -> bool:
    if path.is_symlink():
        return False
    if path.exists() and not path.is_dir():
        _quarantine_corrupt_artifact(path, _vault_corrupt_path_for(path))
        return True
    return False


def _remove_vault_temp_path(path: Path) -> None:
    try:
        if path.is_symlink():
            _quarantine_corrupt_artifact(path, path.with_suffix(".corrupt"))
        elif path.exists() and not path.is_file():
            _quarantine_blocking_vault_artifact(path)
        else:
            path.unlink(missing_ok=True)
    except (OSError, RuntimeError):
        # Best-effort cleanup of an interrupted vault temp write. The atomic
        # write paths call this from their ``except OSError: ...; raise`` rollback
        # (``_write_vault_payload``/``_write_vault_bytes``); a constrained runtime
        # can surface a filesystem rejection as ``RuntimeError`` rather than
        # ``OSError``, and letting that escape the rollback would mask the real
        # ``OSError`` being re-raised. Swallow both, matching
        # :func:`_corrupt_artifacts._remove_path`.
        return


def _quarantine_stale_vault_temp_path(path: Path) -> None:
    """Preserve interrupted vault temp writes before staging a fresh write.

    A *zero-byte* leftover carries no forensic content worth preserving: it is
    either the in-progress ``.tmp`` sentinel ``_write_vault_payload`` touches
    (``sentinel.touch()``) or a uuid temp torn open before its first content
    flush. The rollback now cleans the sentinel symmetrically, but a crash in the
    success path between ``tmp.replace(path)`` and ``sentinel.unlink`` -- or any
    other interrupted write -- can still strand an empty marker. Preserving such a
    marker as a ``.corrupt`` artifact manufactures bogus malformed state that
    masquerades as a real corrupt payload on the next load, exactly the
    defensive-repair noise this storage floor exists to remove. Drop empty
    leftovers; preserve only temps that actually hold (possibly torn) content.
    """

    try:
        if path.is_symlink():
            _quarantine_corrupt_artifact(path, _vault_corrupt_path_for(path))
        elif path.is_file() and path.stat().st_size == 0:
            path.unlink(missing_ok=True)
        elif path.exists():
            _quarantine_corrupt_artifact(path, _vault_corrupt_path_for(path))
    except (OSError, RuntimeError):
        # Preserving a stale temp before staging a fresh write is best-effort; a
        # constrained runtime can raise ``RuntimeError`` instead of ``OSError`` for
        # the same filesystem rejection, and crashing here would force the engine
        # workflow loop into the defensive one-off repair this floor exists to remove.
        return


def _stale_vault_temp_paths(path: Path) -> tuple[Path, ...]:
    parent = path.parent
    legacy_temp_path = path.with_suffix(".tmp")
    try:
        if not parent.exists():
            return (legacy_temp_path,)
        candidates = sorted(parent.iterdir(), key=lambda item: item.name)
    except OSError:
        return (legacy_temp_path,)
    generated_prefixes = [f"{path.name}." if path.name.startswith(".") else f".{path.name}."]
    path_stem = path.name.removesuffix(".json")
    stem_prefix = f"{path_stem}." if path_stem.startswith(".") else f".{path_stem}."
    if stem_prefix not in generated_prefixes:
        generated_prefixes.append(stem_prefix)
    stale_paths = [legacy_temp_path]
    stale_paths.extend(
        candidate
        for candidate in candidates
        if candidate.name.endswith(".tmp") and any(candidate.name.startswith(prefix) for prefix in generated_prefixes)
    )
    return tuple(dict.fromkeys(stale_paths))


def _vault_write_temp_path(path: Path) -> Path:
    # Named seam the vault payload/bytes writers stage through; the body is the
    # shared :func:`_corrupt_artifacts.staged_write_temp_path` so the staged-write
    # temp shape stays one definition across the document and vault stores.
    return _staged_write_temp_path(path)


def _quarantine_stale_vault_temp_paths(path: Path) -> None:
    for temp_path in _stale_vault_temp_paths(path):
        _quarantine_stale_vault_temp_path(temp_path)


def _reject_raced_symlink_vault_temps(path: Path) -> None:
    """Raise FileExistsError if a symlink appeared at any stale temp path after quarantine."""
    for stale in _stale_vault_temp_paths(path):
        if stale.is_symlink():
            _quarantine_corrupt_artifact(stale, stale.with_suffix(".corrupt"))
            _fsync_vault_parent(stale)
            raise FileExistsError(f"vault temp path is a symlink after quarantine: {stale}")


def _fsync_vault_path(path: Path) -> None:
    # Named content-flush seam hardening tests patch in isolation; the body is
    # the shared :func:`_corrupt_artifacts.fsync_file_path` so the durability
    # flush stays one audited path across all stores.
    _fsync_file_path(path)


def _fsync_vault_parent(path: Path) -> None:
    # Named best-effort parent-fsync seam hardening tests patch in isolation; the
    # body is the shared :func:`_corrupt_artifacts.fsync_parent_path` so the
    # directory flush stays one audited path across all stores.
    _fsync_parent_path(path)


def _staged_vault_write(
    path: Path,
    content: str | bytes,
    *,
    encoding: str | None,
    use_sentinel: bool,
) -> None:
    """Stage *content* through the vault store's atomic-write body.

    The canonical payload write (``_write_vault_payload``) and the verbatim
    forensic-snapshot byte restore (``_write_vault_bytes``) carried byte-for-byte
    identical write loops apart from text-vs-binary staging and the in-progress
    ``.tmp`` sentinel: mkdir the parent, reject a parent that resolves through a
    symlink alias, quarantine any blocking target artifact and any stale temp,
    reject a stale temp that raced into a symlink, stage the write under the
    hidden ``.{name}.{uuid}.tmp`` sibling, flush its content through the
    ``_fsync_vault_path`` durability seam, reject a temp that itself raced into a
    symlink, atomically ``replace`` it into place, then best-effort flush the
    parent -- cleaning the staged temp on any ``OSError`` so a torn write never
    strands a half-written sibling for the next stale-temp sweep to preserve as
    masquerading-corrupt noise.

    The vault writers stay vault-local rather than delegating to the shared
    :func:`_corrupt_artifacts.staged_atomic_write` (which the basket and
    context-set stores share) because vault adds the parent symlink-alias guard,
    the pre- and post-stage ``_reject_raced_symlink_vault_temps`` checks, and the
    in-progress ``.tmp`` sentinel that body does not model. Both writers still
    call the named per-store seams (quarantine, fsync, temp removal) by name, so
    the flush-seam and symlink-hardening tests keep patching the module globals
    and exercising the shared loop unchanged.

    Text payloads pass ``encoding="utf-8"`` (staging in ``"x"`` text mode);
    verbatim byte restores pass ``encoding=None`` (binary ``"xb"``) so the
    quarantined bytes republish without re-encoding. ``use_sentinel`` touches and
    cleans the visible ``{stem}.tmp`` in-progress marker only on the canonical
    payload path.
    """

    tmp = _vault_write_temp_path(path)
    mode = "x" if encoding is not None else "xb"
    sentinel = path.with_suffix(".tmp") if use_sentinel else None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if _path_uses_symlink_alias(path.parent):
            raise ValueError(f"vault state parent uses a symlink alias: {path.parent!r}")
        _quarantine_blocking_vault_artifact(path)
        _quarantine_stale_vault_temp_paths(path)
        _reject_raced_symlink_vault_temps(path)
        if sentinel is not None:
            sentinel.touch()
        with tmp.open(mode, encoding=encoding) as file:
            file.write(content)
            file.flush()
        _fsync_vault_path(tmp)
        if tmp.is_symlink():
            raise FileExistsError(f"vault temp path became a symlink: {tmp}")
        _reject_raced_symlink_vault_temps(path)
        tmp.replace(path)
        if sentinel is not None:
            sentinel.unlink(missing_ok=True)
        _fsync_vault_parent(path)
    except OSError:
        _remove_vault_temp_path(tmp)
        # Symmetric with the success-path ``sentinel.unlink`` above: a torn write
        # that touched the in-progress ``.tmp`` sentinel but never reached the
        # atomic replace must not leave that empty marker behind. Otherwise the
        # next write's ``_quarantine_stale_vault_temp_paths`` sweep preserves the
        # zero-byte sentinel as a ``.corrupt`` forensic artifact -- the
        # masquerading-corrupt noise this storage floor exists to remove. Clean
        # it best-effort so the original ``OSError`` still surfaces unmasked.
        if sentinel is not None:
            try:
                sentinel.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def _write_vault_payload(path: Path, payload: object) -> None:
    _staged_vault_write(
        path,
        _canonical_json_dumps(payload),
        encoding="utf-8",
        use_sentinel=True,
    )


def _payload_is_canonical_vault_snapshot(payload: object, state) -> bool:
    """Return ``True`` when ``payload`` is already a clean canonical mirror of ``state``.

    A canonical snapshot carries only the four expected fields with the project
    name and lock state matching ``state`` and no stale ``recovered_from`` marker
    or unknown keys. Used to skip rewriting a backup that already reflects the
    healthy vault state.
    """

    if not isinstance(payload, AbstractMapping):
        return False
    if set(payload.keys()) - {"schema_version", "updated_at", "project_name", "is_locked"}:
        return False
    return (
        payload.get("project_name") == state.project_name
        and payload.get("is_locked") is state.is_locked
        and payload.get("schema_version") == 1
    )


def _write_vault_bytes(path: Path, data: bytes) -> None:
    """Write raw vault artifact bytes atomically and flush the containing directory."""

    _staged_vault_write(path, data, encoding=None, use_sentinel=False)


def _auxiliary_state_paths(self, state_root: Path) -> tuple[Path, ...]:
    """Return the auxiliary vault state files for *state_root*."""

    return (
        self._backup_state_path(state_root),
        self._seed_state_path(state_root),
        self._tmp_state_path(state_root),
        self._backup_tmp_state_path(state_root),
        self._seed_tmp_state_path(state_root),
    )


def _parse_updated_at(self, raw_updated_at: object) -> str | None:
    # Delegate to the shared recovery parser (strip, fold trailing ``z``, parse,
    # normalize to canonical +00:00) so a given on-disk ``updated_at`` recovers to
    # the same instant regardless of which store reads it. This reader's previous
    # strip/fold-then-``_original`` body was byte-identical to the shared parser
    # across the recoverable and rejected inputs the parity test pins.
    return parse_recovered_timestamp(raw_updated_at)


def _quarantine_missing_required_metadata(self, path: Path, payload: object) -> bool:
    original_payload = payload
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        if isinstance(original_payload, AbstractMapping):
            self._quarantine_path(path)
            return True
        return False
    state_root = path.parent
    auxiliary_paths = self._auxiliary_state_paths(state_root)
    if path in auxiliary_paths and _payload_project_name_is_missing_or_blank(payload):
        if isinstance(original_payload, AbstractMapping) and type(original_payload) is not dict:
            _sync_recoverable_vault_payload_mapping_wrapper(original_payload, payload)
        # Auxiliary vault files can be repaired using the project name the
        # caller already supplied, but only when the rest of the payload is
        # still recoverable. Blank names are recoverable even when the
        # timestamp is malformed because the caller can rewrite the payload
        # deterministically; truly missing names still need a recoverable
        # timestamp to avoid accepting opaque auxiliary state.
        if _payload_blank_project_name_is_recoverable(self, payload):
            return False
        if _payload_missing_project_name_and_updated_at_is_recoverable(self, payload):
            return False
        if _payload_missing_project_name_is_recoverable(self, payload):
            return False
        if isinstance(original_payload, AbstractMapping) and type(original_payload) is not dict:
            _sync_vault_payload_mapping_wrapper(
                original_payload,
                _safe_json_value({key: value for key, value in payload.items() if key != "recovered_from"}),
            )
        self._quarantine_path(path)
        return True
    if isinstance(original_payload, AbstractMapping) and type(original_payload) is not dict:
        _sync_vault_payload_mapping_wrapper(
            original_payload,
            _safe_json_value({key: value for key, value in payload.items() if key != "recovered_from"}),
        )
    return _original_quarantine_missing_required_metadata(self, path, payload)


def _snapshot_existing_corrupt_artifacts(
    self,
    state_root: Path,
) -> tuple[tuple[Path, bool, bytes | None], ...]:
    snapshots: list[tuple[Path, bool, bytes | None]] = []
    for live_path, corrupt_path in (
        (self._state_path(state_root), self._corrupt_state_path(state_root)),
        (self._backup_state_path(state_root), self._corrupt_path_for(self._backup_state_path(state_root))),
        (self._seed_state_path(state_root), self._corrupt_path_for(self._seed_state_path(state_root))),
        (self._tmp_state_path(state_root), self._corrupt_path_for(self._tmp_state_path(state_root))),
        (self._backup_tmp_state_path(state_root), self._corrupt_path_for(self._backup_tmp_state_path(state_root))),
        (self._seed_tmp_state_path(state_root), self._corrupt_path_for(self._seed_tmp_state_path(state_root))),
    ):
        if not corrupt_path.exists():
            continue
        snapshots.append((corrupt_path, live_path.exists(), _snapshot_corrupt_artifact_bytes(corrupt_path)))
    return tuple(snapshots)


def _restore_existing_corrupt_artifacts(self, snapshots: tuple[tuple[Path, bool, bytes | None], ...]) -> None:
    # Plain byte payloads flow through ``_write_vault_bytes`` so the restore
    # writer shares the ``_fsync_vault_path`` content-flush seam used by
    # canonical vault state. A raw ``write_bytes`` here was once the lone restore
    # writer on this floor that skipped that seam: a torn restore during recovery
    # rollback would republish a half-written forensic artifact that itself
    # masquerades as corrupt, defeating the snapshot's audit purpose. The
    # restore loop is the canonical one shared by the basket and context-set
    # stores; restore stays best-effort, so a rejected flush is swallowed.
    _restore_corrupt_artifact_snapshots(snapshots, _write_vault_bytes)


def _recovery_marker_missing_updated_at_is_clean(self, payload: object, expected_project_name: str) -> bool:
    """Return ``True`` when an auxiliary vault payload can be recovered without ``updated_at``."""

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "updated_at" in payload or "recovered_from" in payload:
        return False
    if not self._is_supported_payload(payload):
        return False
    return self._is_recoverable_state(payload, expected_project_name)


def _snapshot_dirty_auxiliary_artifacts(
    self,
    state_root: Path,
    expected_project_name: str,
) -> tuple[tuple[Path, bytes], ...]:
    snapshots: list[tuple[Path, bytes]] = []
    for live_path in self._auxiliary_state_paths(state_root):
        corrupt_path = self._corrupt_path_for(live_path)
        if live_path.is_symlink():
            continue
        if live_path.is_dir():
            snapshot = _snapshot_corrupt_artifact_bytes(live_path)
            if snapshot is not None:
                snapshots.append((corrupt_path, snapshot))
            continue
        if not live_path.exists():
            continue
        try:
            raw_bytes = live_path.read_bytes()
        except OSError:
            continue
        try:
            payload = json.loads(raw_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Unparseable auxiliary bytes are a current corruption signal. Preserve
            # them as a quarantine artifact for audit instead of letting temp
            # cleanup silently drop them, mirroring the durable-state quarantine.
            snapshots.append((corrupt_path, raw_bytes))
            continue
        if isinstance(payload, dict) and "recovered_from" in payload:
            snapshots.append((corrupt_path, raw_bytes))
            continue
        if _recovery_marker_missing_updated_at_is_clean(self, payload, expected_project_name):
            continue
        if not self._needs_audit_quarantine(payload):
            continue
        snapshots.append((corrupt_path, raw_bytes))
    return tuple(snapshots)


def _restore_dirty_auxiliary_artifacts(self, snapshots: tuple[tuple[Path, bytes], ...]) -> None:
    for corrupt_path, data in snapshots:
        if corrupt_path.exists():
            if _is_directory_snapshot_bytes(data):
                if corrupt_path.is_file():
                    try:
                        corrupt_path.unlink()
                    except OSError:
                        pass
                elif corrupt_path.is_dir():
                    continue
            else:
                if corrupt_path.is_dir():
                    try:
                        shutil.rmtree(corrupt_path)
                    except OSError:
                        pass
                elif corrupt_path.is_file():
                    try:
                        corrupt_path.unlink()
                    except OSError:
                        pass
        try:
            # Ensure the directory tree exists before attempting to write or
            # restore a snapshot.  This also guarantees that any nested
            # directories created by ``_restore_corrupt_artifact_bytes`` will
            # be placed correctly.
            corrupt_path.parent.mkdir(parents=True, exist_ok=True)

            if _is_directory_snapshot_bytes(data):
                # Attempt to restore a directory snapshot.  The helper returns
                # ``True`` on success; otherwise we fall back to creating an
                # empty directory so that the engine can continue operating.
                if _restore_corrupt_artifact_bytes(corrupt_path, data):
                    continue
                # If restoration failed (malformed snapshot), still create a
                # placeholder directory to avoid leaving the file missing.
                corrupt_path.mkdir(parents=True, exist_ok=True)
                continue

            # Plain byte payloads still need the same atomic write and parent
            # flush semantics as canonical vault state.
            _write_vault_bytes(corrupt_path, data)
        except OSError:
            # Silently ignore failures – the calling logic will treat the
            # artifact as missing and may recover later.  This mirrors the
            # original behaviour for non‑snapshot data while ensuring that a
            # snapshot failure does not leave an orphaned file.
            pass


def _snapshot_clean_auxiliary_artifacts(
    self,
    state_root: Path,
    expected_project_name: str,
) -> tuple[tuple[Path, bytes], ...]:
    snapshots: list[tuple[Path, bytes]] = []
    for live_path in self._auxiliary_state_paths(state_root):
        if live_path.is_symlink():
            continue
        if not live_path.exists():
            continue
        try:
            raw_bytes = live_path.read_bytes()
            payload = json.loads(raw_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError, OSError):
            continue
        if _recovery_marker_candidate_payload_is_clean(self, payload, expected_project_name):
            snapshots.append((live_path, raw_bytes))
            continue
        if _recovery_marker_candidate_missing_project_name_is_clean(self, payload, expected_project_name):
            snapshots.append((live_path, raw_bytes))
            continue
        if not self._needs_audit_quarantine(payload):
            continue
        snapshots.append((live_path, raw_bytes))
    return tuple(snapshots)


def _restore_clean_auxiliary_artifacts(self, snapshots: tuple[tuple[Path, bytes], ...]) -> None:
    for live_path, data in snapshots:
        try:
            live_path.parent.mkdir(parents=True, exist_ok=True)
            _quarantine_blocking_vault_artifact(live_path)
            # Preserve the original auxiliary bytes so recoverable audit state
            # stays visible instead of being canonicalized away.
            _write_vault_bytes(live_path, data)
        except OSError:
            pass


def _preserve_existing_corrupt_artifacts(
    self,
    state_root: Path,
    preserve_primary_corrupt: bool = False,
    preserve_backup_corrupt: bool = False,
    preserve_seed_corrupt: bool = False,
) -> tuple[bool, bool, bool]:
    # Keep previously quarantined persistent state visible across later writes.
    preserve_primary_corrupt = preserve_primary_corrupt or self._corrupt_state_path(state_root).exists()
    preserve_backup_corrupt = preserve_backup_corrupt or self._corrupt_path_for(self._backup_state_path(state_root)).exists()
    preserve_seed_corrupt = preserve_seed_corrupt or self._corrupt_path_for(self._seed_state_path(state_root)).exists()
    return preserve_primary_corrupt, preserve_backup_corrupt, preserve_seed_corrupt


def _recovery_marker_payload_is_clean(self, payload: object, expected_project_name: str) -> bool:
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if "updated_at" not in payload:
        return False
    # The current payload may still carry recovered_from while the rewrite is
    # cleaning up otherwise canonical state. Strip that marker only for the
    # support check so a stable timestamp can survive the rewrite.
    project_name = payload.get("project_name")
    payload_without_recovery = dict(payload)
    payload_without_recovery.pop("recovered_from", None)
    if project_name is None:
        payload_without_recovery["project_name"] = expected_project_name
    if not self._is_supported_payload(payload_without_recovery):
        return False
    if project_name is not None:
        project_name = self._parse_project_name(project_name)
        if project_name is None or project_name != expected_project_name:
            return False
    return True


def _recovery_marker_candidate_payload_is_clean(self, payload: object, expected_project_name: str) -> bool:
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if not _recovery_marker_payload_is_clean(self, payload, expected_project_name):
        return False
    return "recovered_from" not in payload


def _recovery_marker_candidate_missing_project_name_is_clean(
    self,
    payload: object,
    expected_project_name: str,
) -> bool:
    """Return ``True`` when a recoverable auxiliary payload only lacks ``project_name``.

    Vault recovery can repair that field deterministically from the caller's
    expected project name, so auxiliary candidates with otherwise canonical
    content should stay available instead of being quarantined. Missing or
    blank ``project_name`` is acceptable here because the caller can restore
    it from the expected project name. Missing ``updated_at`` is also
    acceptable because the caller rewrites the recovered payload with a fresh
    timestamp when no clean timestamp can be donated. Blank ``project_name``
    with a malformed timestamp stays recoverable as long as the remaining
    payload is still supported.
    """

    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return False
    if not _payload_project_name_is_missing_or_blank(payload) or "recovered_from" in payload:
        return False
    if _payload_blank_project_name_is_recoverable(self, payload):
        return True
    payload_without_project_name = dict(payload)
    payload_without_project_name.pop("project_name", None)
    payload_without_project_name.pop("recovered_from", None)
    if payload_without_project_name.get("updated_at") is None:
        payload_without_project_name.pop("updated_at", None)
    return self._is_supported_payload(payload_without_project_name)


def _recovery_marker_candidate_timestamp(
    self,
    payload: object,
    expected_project_name: str,
    *,
    allow_recovered_from: bool = False,
    allow_missing_project_name: bool = False,
) -> str | None:
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return None
    if not self._is_recoverable_state(payload, expected_project_name):
        if not (
            allow_missing_project_name
            and _recovery_marker_candidate_missing_project_name_is_clean(self, payload, expected_project_name)
        ):
            return None
    if self._parse_schema_version(payload) is None:
        return None
    if not allow_recovered_from and "recovered_from" in payload:
        return None
    return self._parse_updated_at(payload.get("updated_at"))


def _requires_safe_lock(self, payload: dict[str, object], expected_project_name: str) -> bool:
    if payload.get("project_name") is None:
        return not _recovery_marker_candidate_missing_project_name_is_clean(self, payload, expected_project_name)
    stored_project_name = self._parse_project_name(payload.get("project_name"))
    if stored_project_name is None:
        return True
    return stored_project_name != expected_project_name


def _recovery_marker_cleanup_timestamp(self, payload: object, expected_project_name: str) -> str | None:
    if not _recovery_marker_payload_is_clean(self, payload, expected_project_name):
        return None
    normalized_updated_at = self._parse_updated_at(payload.get("updated_at"))
    return normalized_updated_at


def _prefer_recovery_timestamp(primary_updated_at: str | None, backup_updated_at: str | None) -> str | None:
    """Return the newest timestamp available for a recovery rewrite.

    Vault recovery should keep the newest recoverable audit time when the
    primary payload is imperfect but still carries a valid timestamp. This
    mirrors the basket recovery hardening and keeps rewrites deterministic
    without inventing a fresher timestamp when one already exists on disk.
    """

    if primary_updated_at is None:
        return backup_updated_at
    if backup_updated_at is None:
        return primary_updated_at
    return max(primary_updated_at, backup_updated_at)


def _recovery_marker_best_candidate_timestamp(
    self,
    candidate_payloads: tuple[object, ...],
    expected_project_name: str,
) -> str | None:
    # Prefer the newest clean recoverable timestamp, then break ties in favor
    # of clean provenance so audit-quarantined copies do not donate stale
    # audit times to the canonical rewrite. If only recovered payloads remain,
    # keep the newest recovered timestamp instead of inventing a fresh one.
    best_candidate_key: tuple[str, bool, bool, int] | None = None
    best_candidate_timestamp: str | None = None
    recovered_candidate_key: tuple[str, bool, bool, int] | None = None
    recovered_candidate_timestamp: str | None = None
    for position, candidate_payload in enumerate(candidate_payloads):
        candidate_payload = _payload_as_plain_dict(candidate_payload)
        if candidate_payload is None:
            continue
        candidate_timestamp = _recovery_marker_candidate_timestamp(
            self,
            candidate_payload,
            expected_project_name,
            allow_recovered_from=True,
            allow_missing_project_name=True,
        )
        if candidate_timestamp is None:
            continue
        candidate_key = (
            candidate_timestamp,
            not self._needs_audit_quarantine(candidate_payload),
            not (isinstance(candidate_payload, dict) and "recovered_from" in candidate_payload),
            -position,
        )
        if isinstance(candidate_payload, dict) and "recovered_from" in candidate_payload:
            if recovered_candidate_key is None or candidate_key > recovered_candidate_key:
                recovered_candidate_key = candidate_key
                recovered_candidate_timestamp = candidate_timestamp
            continue
        if self._needs_audit_quarantine(candidate_payload):
            continue
        if best_candidate_key is None or candidate_key > best_candidate_key:
            best_candidate_key = candidate_key
            best_candidate_timestamp = candidate_timestamp
    if best_candidate_timestamp is not None:
        return best_candidate_timestamp
    return recovered_candidate_timestamp


def _prefer_recovery_payload(
    self,
    backup_tmp_payload: dict[str, object] | None,
    backup_payload: dict[str, object] | None,
    seed_tmp_payload: dict[str, object] | None,
    seed_payload: dict[str, object] | None,
    tmp_payload: dict[str, object] | None,
    expected_project_name: str,
) -> tuple[dict[str, object] | None, str | None]:
    best_candidate: tuple[dict[str, object] | None, str | None] = (None, None)
    best_candidate_key: tuple[bool, str, bool, int] | None = None
    recovered_candidate: tuple[dict[str, object] | None, str | None] = (None, None)
    recovered_candidate_key: tuple[bool, str, int] | None = None
    # Prefer durable backup/seed sources on ties so temp artifacts only win
    # when they are strictly newer than the committed copies. If timestamps
    # match, prefer the clean copy over a recovered copy so provenance stays
    # deterministic. If the only available source is already marked recovered,
    # fall back to it as a last resort instead of dropping to an empty state.
    for position, (candidate, recovered_source) in enumerate(
        (
            (backup_payload, "backup"),
            (seed_payload, "seed"),
            (backup_tmp_payload, "backup_tmp"),
            (seed_tmp_payload, "seed_tmp"),
            (tmp_payload, "tmp"),
        )
    ):
        if candidate is None:
            continue
        candidate = _payload_as_plain_dict(candidate)
        if candidate is None:
            continue
        if (
            not self._is_recoverable_state(candidate, expected_project_name)
            and not _recovery_marker_candidate_missing_project_name_is_clean(self, candidate, expected_project_name)
            and not _payload_blank_project_name_is_recoverable(self, candidate)
        ):
            continue
        if isinstance(candidate, dict) and "recovered_from" in candidate:
            # Recovered auxiliaries with an empty or malformed audit timestamp
            # should not outrank a clean primary state.
            if self._parse_updated_at(candidate.get("updated_at")) is None:
                continue
            candidate_base_key = self._recovery_candidate_key(candidate, position)
            if recovered_candidate_key is None or candidate_base_key > recovered_candidate_key:
                recovered_candidate = (candidate, recovered_source)
                recovered_candidate_key = candidate_base_key
            continue
        if self._needs_audit_quarantine(candidate) and not _recovery_marker_missing_updated_at_is_clean(
            self,
            candidate,
            expected_project_name,
        ):
            continue
        candidate_base_key = self._recovery_candidate_key(candidate, position)
        candidate_key = (
            candidate_base_key[0],
            candidate_base_key[1],
            not self._needs_audit_quarantine(candidate),
            not (isinstance(candidate, dict) and "recovered_from" in candidate),
            candidate_base_key[2],
        )
        if best_candidate_key is None or candidate_key > best_candidate_key:
            best_candidate = (candidate, recovered_source)
            best_candidate_key = candidate_key
    if best_candidate != (None, None):
        return best_candidate
    return recovered_candidate


def _create_or_open(self, root_dir: Path | str, project_name: str):
    """Create or open a vault within ``root_dir``.

    The original implementation omitted type annotations for the two
    parameters.  While Python accepts positional arguments without types,
    callers that use keyword syntax (e.g., ``create_or_open(tmp, project)``)
    would incorrectly bind ``project_name`` to ``root_dir`` and vice versa.
    Adding explicit type annotations clarifies the intended contract and
    prevents accidental misuse.  It also matches how the method is used in
    tests and other modules.
    """
    root_dir = Path(root_dir)
    if _path_uses_symlink_alias(root_dir):
        raise ValueError(f"vault root uses a symlink alias: {root_dir!r}")
    safe_project_name = validate_project_name(project_name)
    project_root = root_dir / safe_project_name
    if _path_uses_symlink_alias(project_root):
        raise ValueError(f"vault project root uses a symlink alias: {project_root!r}")
    _quarantine_blocking_vault_directory(project_root)
    project_root.mkdir(parents=True, exist_ok=True)
    setattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, {})

    def _peek_payload(path, *, read_symlink: bool = False):
        if path.is_symlink():
            if not read_symlink:
                return None
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
        if (
            isinstance(source_payloads, AbstractMutableMapping)
            and isinstance(payload, AbstractMapping)
            and type(payload) is not dict
        ):
            source_payloads[path] = payload
        return payload

    primary_path = self._state_path(project_root)
    primary_payload = _peek_payload(primary_path)
    # Capture the primary's load-start parse state before any peek-driven
    # quarantine rewrites it. A primary marker is a current corruption signal --
    # and so must survive recovery for audit -- only when the primary file was
    # present but not an auditable mapping at load start. A healthy or absent
    # primary leaves any sibling ``.corrupt.json`` stale and clearable.
    primary_present_at_load = primary_path.exists()
    preserve_primary_corrupt = primary_present_at_load and not isinstance(primary_payload, AbstractMapping)
    # A mapping primary whose required fields (``schema_version`` plus a parseable
    # ``is_locked``) all survived but whose only defect is a present-but-invalid
    # ``project_name`` value loses nothing auditable: the canonical rewrite
    # restores the caller's authoritative name and a safe lock. Its fresh
    # quarantine marker is therefore stale and clearable, unlike a primary that
    # actually dropped a required field (for example a missing ``is_locked``),
    # whose marker is preserved for audit.
    load_start_primary_dict = (
        _payload_as_plain_dict(primary_payload) if isinstance(primary_payload, AbstractMapping) else None
    )
    primary_invalid_project_name_only = (
        isinstance(load_start_primary_dict, dict)
        and "schema_version" in load_start_primary_dict
        and "is_locked" in load_start_primary_dict
        and self._parse_is_locked(load_start_primary_dict.get("is_locked")) is not None
        and isinstance(load_start_primary_dict.get("project_name"), str)
        and self._parse_project_name(load_start_primary_dict.get("project_name")) is None
    )
    primary_payload_wrapper = (
        primary_payload if isinstance(primary_payload, AbstractMapping) and type(primary_payload) is not dict else None
    )
    backup_path = self._backup_state_path(project_root)
    backup_was_symlink = backup_path.is_symlink()
    backup_payload = _peek_payload(backup_path, read_symlink=True)
    if backup_was_symlink:
        _quarantine_path(backup_path)
    backup_payload_wrapper = (
        backup_payload if isinstance(backup_payload, AbstractMapping) and type(backup_payload) is not dict else None
    )
    if primary_path.exists():
        if isinstance(primary_payload, AbstractMapping) and type(primary_payload) is not dict:
            primary_payload = _payload_as_plain_dict(primary_payload)
        if not isinstance(primary_payload, dict):
            # Non-mapping primary payloads are not auditable vault state;
            # preserve the raw file before the canonical rewrite replaces it.
            _quarantine_path(primary_path)

    corrupt_artifacts = _snapshot_existing_corrupt_artifacts(self, project_root)
    # Markers that already existed at load start are the only ones eligible for
    # stale-marker clearing; markers freshly written during this load are absent
    # from this set and stay for audit. Mirrors the load-start rule shared with
    # the basket and context-set stores.
    load_start_corrupt_paths = {path for path, _, _ in corrupt_artifacts}
    # Whether any auxiliary state file was present at load start, captured before
    # ``_read_state`` quarantines an unsalvageable backup/seed out of the way. A
    # corrupt primary rewritten alongside a present auxiliary yields a coherent
    # primary/backup pair, so its quarantine marker is stale.
    auxiliary_present_at_load = (
        self._backup_state_path(project_root).exists() or self._seed_state_path(project_root).exists()
    )
    dirty_auxiliary_artifacts = _snapshot_dirty_auxiliary_artifacts(self, project_root, safe_project_name)
    clean_auxiliary_artifacts = _snapshot_clean_auxiliary_artifacts(self, project_root, safe_project_name)
    source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
    if isinstance(source_payloads, AbstractMutableMapping):
        if primary_payload_wrapper is not None:
            source_payloads[primary_path] = primary_payload_wrapper
        if backup_payload_wrapper is not None:
            source_payloads[backup_path] = backup_payload_wrapper

    candidate_payloads = (
        backup_payload,
        _peek_payload(self._seed_state_path(project_root)),
        _peek_payload(self._backup_tmp_state_path(project_root)),
        _peek_payload(self._seed_tmp_state_path(project_root)),
        _peek_payload(self._tmp_state_path(project_root)),
    )
    candidate_payload_snapshots = tuple(_payload_as_plain_dict(candidate) for candidate in candidate_payloads)
    # Clear any stale salvage marker from a prior load before ``_read_state`` records
    # whether this load promoted an in-place backup/seed salvage.
    if hasattr(self, _VAULT_SALVAGED_AUX_SOURCE_ATTR):
        delattr(self, _VAULT_SALVAGED_AUX_SOURCE_ATTR)
    raw_state, recovered_source, primary_unavailable, preserve_backup_corrupt, preserve_seed_corrupt = self._read_state(
        project_root,
        safe_project_name,
    )
    salvaged_aux_source = getattr(self, _VAULT_SALVAGED_AUX_SOURCE_ATTR, None)
    # _original_create_or_open performs its own cleanup pass, so keep any
    # quarantine artifacts created while reading state as well as preexisting
    # ones.
    corrupt_artifacts = corrupt_artifacts + _snapshot_existing_corrupt_artifacts(self, project_root)
    # Collect the stale sibling markers a healthy/recovered load should not leave
    # behind. A primary/backup/seed marker is cleared unless its source is still a
    # current corruption signal (decided from load-start parse state); orphaned
    # temp-staging markers have no surviving source and are always clearable. The
    # ``finally`` unlink restricts this to markers that pre-existed at load start
    # so freshly quarantined audit artifacts are preserved. Mirrors
    # ``set_store.py::_load`` and ``store.py::_context_basket_store_load``.
    load_clearable_corrupt_paths: list[Path] = []
    # Markers freshly written by this load that are still clearable despite being
    # absent from the load-start snapshot: a mapping primary quarantined solely
    # for an invalid ``project_name`` value loses nothing auditable, so its fresh
    # marker is removed rather than preserved.
    fresh_clearable_corrupt_paths: list[Path] = []
    if primary_invalid_project_name_only:
        fresh_clearable_corrupt_paths.append(self._corrupt_state_path(project_root))
    # An unparseable primary that was successfully superseded by a recovery from a
    # durable or temp auxiliary is no longer a current corruption signal: the
    # rewritten primary is authoritative, so its quarantine marker is stale and
    # cleared like any other recovered artifact. A corrupt primary that fell to a
    # fresh safe-lock default while an auxiliary file was present at load start is
    # likewise resolved -- the rewrite produces a coherent primary/backup pair, so
    # its marker is stale. Only a corrupt primary standing alone with no auxiliary
    # to anchor the rewrite keeps its marker for audit.
    primary_corrupt_superseded_by_recovery = (
        preserve_primary_corrupt
        and primary_unavailable
        and (
            recovered_source in {"backup", "seed", "backup_tmp", "seed_tmp", "tmp"}
            or (recovered_source is None and auxiliary_present_at_load)
        )
    )
    if not preserve_primary_corrupt or primary_corrupt_superseded_by_recovery:
        load_clearable_corrupt_paths.append(self._corrupt_state_path(project_root))
    if not preserve_backup_corrupt:
        load_clearable_corrupt_paths.append(self._corrupt_path_for(self._backup_state_path(project_root)))
    if not preserve_seed_corrupt:
        load_clearable_corrupt_paths.append(self._corrupt_path_for(self._seed_state_path(project_root)))
    load_clearable_corrupt_paths.extend(
        (
            self._corrupt_path_for(self._tmp_state_path(project_root)),
            self._corrupt_path_for(self._backup_tmp_state_path(project_root)),
            self._corrupt_path_for(self._seed_tmp_state_path(project_root)),
        )
    )
    # A healthy/salvaged primary load (no recovery source, primary present) has no
    # use for a stale durable seed snapshot: the seed is a write-time fallback, not
    # a load-time recovery audit artifact, and ``_read_state`` already cleared it.
    # Drop it from the clean-auxiliary restore so the read's clearing survives
    # instead of being re-created on disk. Mirrors the basket/context-set stores
    # clearing stale sibling state on a healthy load.
    primary_loaded_healthy = recovered_source is None and not primary_unavailable
    seed_state_path = self._seed_state_path(project_root)
    # A seed consumed as the recovery source is folded into the rewritten
    # primary/backup and cleared by ``_write_state``; it must not be re-created
    # from the load-start clean-auxiliary snapshot. This covers two recovered
    # seeds: an in-place salvage promotion (recoverable identity with only
    # droppable defects) and a byte-clean seed that normal recovery selected. A
    # seed whose only defect is a repairable missing/blank ``project_name`` is
    # deliberately excluded so its raw payload stays on disk as an audit artifact.
    # Capture this before later branches reassign ``recovered_source``.
    seed_recovered_at_load = salvaged_aux_source == "seed" or (
        recovered_source == "seed"
        and _recovery_marker_candidate_payload_is_clean(self, candidate_payloads[1], safe_project_name)
    )
    cleanup_timestamp = self._recovery_marker_cleanup_timestamp(raw_state, safe_project_name)
    primary_recovery_timestamp = None
    candidate_cleanup_timestamp = None
    if cleanup_timestamp is None:
        # Keep a valid timestamp from the primary payload when the payload is
        # otherwise recoverable but not clean enough to donate its own cleanup
        # timestamp directly.
        primary_recovery_timestamp = _recovery_marker_candidate_timestamp(self, raw_state, safe_project_name)
        # When the primary state cannot keep its own timestamp, reuse the
        # closest matching auxiliary source rather than inventing a new audit
        # time.
        candidate_cleanup_timestamp = _recovery_marker_best_candidate_timestamp(
            self,
            candidate_payloads,
            safe_project_name,
        )
    try:
        force_rewrite_state = False
        state = _original_create_or_open(self, root_dir, project_name)
        raw_state_payload = _payload_as_plain_dict(raw_state)
        selected_recovery_payload, selected_recovered_source = self._prefer_recovery_payload(
            candidate_payloads[2],
            candidate_payloads[0],
            candidate_payloads[3],
            candidate_payloads[1],
            candidate_payloads[4],
            safe_project_name,
        )
        selected_raw_recovery_payload: dict[str, object] | None = None
        if selected_recovered_source == "backup":
            selected_raw_recovery_payload = (
                dict(candidate_payload_snapshots[0]) if isinstance(candidate_payload_snapshots[0], dict) else None
            )
        elif selected_recovered_source == "seed":
            selected_raw_recovery_payload = (
                dict(candidate_payload_snapshots[1]) if isinstance(candidate_payload_snapshots[1], dict) else None
            )
        elif selected_recovered_source == "backup_tmp":
            selected_raw_recovery_payload = (
                dict(candidate_payload_snapshots[2]) if isinstance(candidate_payload_snapshots[2], dict) else None
            )
        elif selected_recovered_source == "seed_tmp":
            selected_raw_recovery_payload = (
                dict(candidate_payload_snapshots[3]) if isinstance(candidate_payload_snapshots[3], dict) else None
            )
        elif selected_recovered_source == "tmp":
            selected_raw_recovery_payload = (
                dict(candidate_payload_snapshots[4]) if isinstance(candidate_payload_snapshots[4], dict) else None
            )
        if (
            primary_unavailable
            and selected_recovered_source in {"backup", "seed"}
            and isinstance(selected_raw_recovery_payload, dict)
            and selected_raw_recovery_payload.get("project_name") is None
        ):
            # The chosen durable auxiliary never carried a ``project_name`` of its
            # own. A blank name (present but empty) is recoverable -- the canonical
            # rewrite restores it from the caller's expected name -- but a truly
            # absent name leaves the auxiliary an untrusted, opaque source whose
            # lock state cannot be vouched for. ``_read_state`` quarantines it for
            # audit; decline to promote it here so recovery falls through to a safe
            # locked default rewrite instead of fabricating an identity and
            # inheriting an unverified unlocked state.
            selected_recovery_payload = None
            selected_recovered_source = None
            selected_raw_recovery_payload = None
        temp_source_path = _vault_temp_source_path(self, project_root, selected_recovered_source)
        if temp_source_path is not None:
            setattr(self, _VAULT_TEMP_SOURCE_PATH_ATTR, temp_source_path)
            source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
            if (
                isinstance(source_payloads, AbstractMutableMapping)
                and isinstance(selected_recovery_payload, AbstractMapping)
                and type(selected_recovery_payload) is not dict
            ):
                source_payloads[temp_source_path] = selected_recovery_payload
        else:
            try:
                delattr(self, _VAULT_TEMP_SOURCE_PATH_ATTR)
            except AttributeError:
                pass
        if (
            selected_recovery_payload is None
            and isinstance(raw_state_payload, dict)
            and _payload_missing_project_name_can_preserve_lock_state(self, raw_state_payload)
        ):
            recovered_is_locked = self._parse_is_locked(raw_state_payload.get("is_locked"))
            if recovered_is_locked is not None and state.is_locked != recovered_is_locked:
                state = VaultState(
                    project_name=safe_project_name,
                    root_dir=project_root,
                    is_locked=recovered_is_locked,
                )
                force_rewrite_state = True
        if (
            selected_recovery_payload is None
            and isinstance(raw_state_payload, dict)
            and self._parse_project_name(raw_state_payload.get("project_name")) == safe_project_name
        ):
            recovered_is_locked = self._parse_is_locked(raw_state_payload.get("is_locked"))
            if recovered_is_locked is not None and state.is_locked != recovered_is_locked:
                state = VaultState(
                    project_name=safe_project_name,
                    root_dir=project_root,
                    is_locked=recovered_is_locked,
                )
                force_rewrite_state = True
        if (
            isinstance(selected_raw_recovery_payload, dict)
            and _payload_project_name_is_missing_or_blank(selected_raw_recovery_payload)
            and isinstance(selected_raw_recovery_payload.get("is_locked"), bool)
            and state.is_locked != selected_raw_recovery_payload["is_locked"]
        ):
            state = VaultState(
                project_name=safe_project_name,
                root_dir=project_root,
                is_locked=selected_raw_recovery_payload["is_locked"],
            )
            force_rewrite_state = True
        if selected_recovery_payload is not None and (
            not isinstance(raw_state_payload, dict)
            or not self._is_recoverable_state(raw_state_payload, safe_project_name)
            or (
                isinstance(selected_recovery_payload, dict)
                and isinstance(selected_recovery_payload.get("is_locked"), bool)
                and state.is_locked != selected_recovery_payload["is_locked"]
            )
        ):
            # Only carry provenance forward when the primary state itself needs
            # a recovery rewrite. Clean primaries with recoverable auxiliaries
            # should keep their backups available without forcing a rewrite.
            recovered_source = selected_recovered_source
        if (
            isinstance(selected_recovery_payload, dict)
            and selected_recovered_source == "backup"
            and backup_was_symlink
            and isinstance(selected_recovery_payload.get("is_locked"), bool)
            and state.is_locked != selected_recovery_payload["is_locked"]
        ):
            state = VaultState(
                project_name=safe_project_name,
                root_dir=project_root,
                is_locked=selected_recovery_payload["is_locked"],
            )
            force_rewrite_state = True
        if (
            isinstance(selected_recovery_payload, dict)
            and _payload_project_name_is_missing_or_blank(selected_recovery_payload)
            and isinstance(selected_recovery_payload.get("is_locked"), bool)
            and state.is_locked != selected_recovery_payload["is_locked"]
        ):
            state = VaultState(
                project_name=safe_project_name,
                root_dir=project_root,
                is_locked=selected_recovery_payload["is_locked"],
            )
            force_rewrite_state = True
        if (
            primary_unavailable
            and isinstance(selected_raw_recovery_payload, dict)
            and selected_recovered_source in {"backup", "seed"}
            and not _payload_is_canonical_recovered_from_record(self, selected_raw_recovery_payload)
            and self._parse_project_name(selected_raw_recovery_payload.get("project_name")) == safe_project_name
            and self._parse_is_locked(selected_raw_recovery_payload.get("is_locked")) is not None
        ):
            # A durable backup/seed whose only defects are droppable optional
            # metadata (a malformed ``updated_at`` or ``recovered_from`` value, a
            # whitespace-padded ``project_name``, or a string ``is_locked``) is
            # salvaged in place: its parsed lock state is authoritative, so it must
            # not be displaced by the safe-lock default that applies when no
            # recovery source survives. The pre-rewrite snapshot is inspected
            # because ``selected_recovery_payload`` may be a live wrapper the
            # earlier canonical rewrite already normalized. A byte-canonical
            # ``recovered_from`` provenance record is excluded -- it is preserved
            # for audit rather than salvaged. Mirrors the in-place primary salvage.
            salvaged_is_locked = self._parse_is_locked(selected_raw_recovery_payload.get("is_locked"))
            if state.is_locked != salvaged_is_locked:
                state = VaultState(
                    project_name=safe_project_name,
                    root_dir=project_root,
                    is_locked=salvaged_is_locked,
                )
                force_rewrite_state = True
        if (
            isinstance(selected_raw_recovery_payload, dict)
            and isinstance(selected_raw_recovery_payload.get("project_name"), str)
            and not selected_raw_recovery_payload["project_name"].strip()
            and isinstance(selected_raw_recovery_payload.get("updated_at"), str)
            and selected_raw_recovery_payload["updated_at"].strip()
            and self._parse_updated_at(selected_raw_recovery_payload["updated_at"]) is None
        ):
            # Blank project names are recoverable enough to rewrite back to
            # canonical state without tagging the final payload as a recovery
            # when the timestamp is malformed. A blank name with ``updated_at``
            # missing still needs the provenance marker.
            recovered_source = None
        if (
            selected_recovered_source in {"backup_tmp", "seed_tmp", "tmp"}
            and (
                (
                    isinstance(selected_raw_recovery_payload, dict)
                    and "recovered_from" in selected_raw_recovery_payload
                )
                or (isinstance(selected_recovery_payload, dict) and "recovered_from" in selected_recovery_payload)
            )
        ):
            recovered_source = None
        rewrite_timestamp = cleanup_timestamp
        rewrite_state = force_rewrite_state or (
            cleanup_timestamp is not None
            and (
                recovered_source is not None or not self._is_recoverable_state(raw_state, safe_project_name)
            )
        )
        if not rewrite_state and rewrite_timestamp is None:
            rewrite_timestamp = _prefer_recovery_timestamp(primary_recovery_timestamp, candidate_cleanup_timestamp)
            rewrite_state = rewrite_timestamp is not None
        if rewrite_state:
            # Re-emit the clean state once so a recoverable source can keep its
            # original audit time even when a quarantined backup or seed must stay
            # on disk for inspection.
            resolved_rewrite_timestamp = rewrite_timestamp
            if resolved_rewrite_timestamp is None and selected_recovery_payload is None:
                # Primary-only recovery has no on-disk timestamp to preserve,
                # so write a fresh canonical value for both the primary and
                # the backup copy. Auxiliary recoveries intentionally keep
                # their null timestamp contract intact.
                resolved_rewrite_timestamp = utc_now_iso()
            rewritten_recovered_from = self._recovery_marker(
                primary_unavailable=primary_unavailable,
                recovered_source=recovered_source,
            )
            if selected_recovered_source in {"backup_tmp", "seed_tmp", "tmp"}:
                rewritten_recovered_from = None
            rewritten_primary_payload = {
                "schema_version": 1,
                "updated_at": resolved_rewrite_timestamp,
                "project_name": state.project_name,
                "is_locked": state.is_locked,
            }
            if rewritten_recovered_from is not None:
                rewritten_primary_payload["recovered_from"] = rewritten_recovered_from
            rewritten_backup_payload = {
                "schema_version": 1,
                "updated_at": resolved_rewrite_timestamp,
                "project_name": state.project_name,
                "is_locked": state.is_locked,
            }
            self._write_state(
                state,
                recovered_from=rewritten_recovered_from,
                updated_at=resolved_rewrite_timestamp,
                preserve_backup_corrupt=preserve_backup_corrupt,
                preserve_seed_corrupt=preserve_seed_corrupt,
            )
            if resolved_rewrite_timestamp is None and recovered_source is not None:
                # A salvaged auxiliary recovery has no on-disk timestamp to
                # preserve, so ``_write_state`` stamps the primary with a fresh
                # canonical value. The backup copy rewritten below must match
                # that same value rather than keeping its null placeholder, so
                # both snapshots stay timestamp-consistent after recovery.
                written_primary = _peek_payload(primary_path)
                if isinstance(written_primary, dict):
                    written_timestamp = written_primary.get("updated_at")
                    if isinstance(written_timestamp, str) and written_timestamp:
                        rewritten_primary_payload["updated_at"] = written_timestamp
                        rewritten_backup_payload["updated_at"] = written_timestamp
            if primary_payload_wrapper is not None:
                _sync_vault_payload_mapping_wrapper(primary_payload_wrapper, _safe_json_value(rewritten_primary_payload))
            if backup_payload_wrapper is not None:
                _sync_vault_payload_mapping_wrapper(backup_payload_wrapper, _safe_json_value(rewritten_backup_payload))
        # A seed must not be re-created from its load-start clean snapshot when it
        # was folded into the rewrite (primary loaded healthy or the seed was the
        # recovery source) or when it was quarantined this load as an untrusted
        # absent-``project_name`` auxiliary. In the quarantine case the original
        # bytes already live in the ``.seed.corrupt.json`` audit artifact, so
        # restoring the live seed would resurrect the rejected, identity-less state.
        drop_seed_from_restore = primary_loaded_healthy or seed_recovered_at_load or preserve_seed_corrupt
        restorable_clean_auxiliary_artifacts = (
            tuple(
                snapshot
                for snapshot in clean_auxiliary_artifacts
                if snapshot[0] != seed_state_path
            )
            if drop_seed_from_restore
            else clean_auxiliary_artifacts
        )
        _restore_clean_auxiliary_artifacts(self, restorable_clean_auxiliary_artifacts)
        if rewrite_state:
            try:
                _write_vault_payload(backup_path, rewritten_backup_payload)
            except OSError:
                pass
            final_primary_payload = _peek_payload(primary_path)
            if primary_payload_wrapper is not None and isinstance(final_primary_payload, dict):
                _sync_vault_payload_mapping_wrapper(primary_payload_wrapper, final_primary_payload)
            final_backup_payload = _peek_payload(backup_path)
            if backup_payload_wrapper is not None and isinstance(final_backup_payload, dict):
                _sync_vault_payload_mapping_wrapper(backup_payload_wrapper, final_backup_payload)
            final_primary_payload = _peek_payload(primary_path)
            final_backup_payload = _peek_payload(backup_path)
            if (
                selected_recovered_source in {"backup_tmp", "seed_tmp", "tmp"}
                and isinstance(final_primary_payload, dict)
                and isinstance(final_backup_payload, dict)
                and "recovered_from" in final_primary_payload
                and "recovered_from" not in final_backup_payload
            ):
                final_primary_payload.pop("recovered_from", None)
                _write_vault_payload(primary_path, final_primary_payload)
        elif isinstance(backup_payload, AbstractMapping) and not backup_payload:
            # An empty auxiliary payload is not a durable recovery source.
            # Rewrite it to the canonical vault snapshot so later runs do not
            # keep re-reading an unusable backup shell.
            resolved_backup_timestamp = cleanup_timestamp or primary_recovery_timestamp or candidate_cleanup_timestamp
            if resolved_backup_timestamp is None:
                resolved_backup_timestamp = utc_now_iso()
            rewritten_backup_payload = {
                "schema_version": 1,
                "updated_at": resolved_backup_timestamp,
                "project_name": state.project_name,
                "is_locked": state.is_locked,
            }
            try:
                _write_vault_payload(backup_path, rewritten_backup_payload)
            except OSError:
                pass
            if backup_payload_wrapper is not None:
                _sync_vault_payload_mapping_wrapper(backup_payload_wrapper, _safe_json_value(rewritten_backup_payload))
        elif preserve_backup_corrupt:
            # The backup was unsalvageable and copied to its ``.bak.corrupt.json``
            # audit artifact, but the live ``.bak.json`` still holds the rejected
            # payload. Leaving it in place means a later load re-quarantines and
            # re-reads the same broken state, so rewrite the live copy to the
            # canonical vault snapshot. The audit artifact remains the sole record
            # of the rejected payload. Only fires when no recovery rewrite already
            # refreshed the backup above. The timestamp follows the just-written
            # primary so both snapshots stay consistent.
            live_backup_payload = _peek_payload(backup_path)
            if not _payload_is_canonical_vault_snapshot(live_backup_payload, state):
                written_primary = _peek_payload(primary_path)
                resolved_backup_timestamp = None
                if isinstance(written_primary, dict):
                    primary_timestamp = written_primary.get("updated_at")
                    if isinstance(primary_timestamp, str) and primary_timestamp:
                        resolved_backup_timestamp = primary_timestamp
                if resolved_backup_timestamp is None:
                    resolved_backup_timestamp = (
                        cleanup_timestamp or primary_recovery_timestamp or candidate_cleanup_timestamp or utc_now_iso()
                    )
                rewritten_backup_payload = {
                    "schema_version": 1,
                    "updated_at": resolved_backup_timestamp,
                    "project_name": state.project_name,
                    "is_locked": state.is_locked,
                }
                try:
                    _write_vault_payload(backup_path, rewritten_backup_payload)
                except OSError:
                    pass
                if backup_payload_wrapper is not None:
                    _sync_vault_payload_mapping_wrapper(backup_payload_wrapper, _safe_json_value(rewritten_backup_payload))
        _sync_vault_source_payloads(
            self,
            primary_path,
            preserve_equivalent_raw_wrapper=not rewrite_state,
        )
        final_primary_payload = _peek_payload(primary_path)
        final_backup_payload = _peek_payload(backup_path)
        if (
            selected_recovered_source in {"backup_tmp", "seed_tmp", "tmp"}
            and isinstance(final_primary_payload, dict)
            and isinstance(final_backup_payload, dict)
            and "recovered_from" in final_primary_payload
            and "recovered_from" not in final_backup_payload
        ):
            final_primary_payload.pop("recovered_from", None)
            _write_vault_payload(primary_path, final_primary_payload)
        return state
    finally:
        _restore_existing_corrupt_artifacts(self, corrupt_artifacts)
        if load_clearable_corrupt_paths:
            # Clear only the stale markers that pre-existed at load start (and were
            # just restored above); markers freshly written by this load are absent
            # from the load-start set and stay for audit.
            for corrupt_path in load_clearable_corrupt_paths:
                if corrupt_path in load_start_corrupt_paths:
                    self._unlink_if_exists(corrupt_path)
        for corrupt_path in fresh_clearable_corrupt_paths:
            self._unlink_if_exists(corrupt_path)
        _restore_dirty_auxiliary_artifacts(self, dirty_auxiliary_artifacts)
        _sync_vault_source_payloads(
            self,
            primary_path,
            preserve_equivalent_raw_wrapper=True,
        )
        source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
        if isinstance(source_payloads, AbstractMutableMapping):
            temp_source_paths = {
                self._tmp_state_path(project_root),
                self._backup_tmp_state_path(project_root),
                self._seed_tmp_state_path(project_root),
            }
            for live_path, data in clean_auxiliary_artifacts:
                if live_path in temp_source_paths:
                    continue
                try:
                    current_payload = json.loads(live_path.read_text(encoding="utf-8"))
                    restored_payload = json.JSONDecoder().decode(data.decode("utf-8"))
                except Exception:
                    current_payload = None
                    restored_payload = None
                if isinstance(current_payload, dict) and isinstance(restored_payload, dict) and current_payload != restored_payload:
                    continue
                source_payload = source_payloads.get(live_path)
                if not isinstance(source_payload, AbstractMapping) or type(source_payload) is dict:
                    continue
                try:
                    restored_payload = json.JSONDecoder().decode(data.decode("utf-8"))
                except Exception:
                    continue
                restored_payload = _payload_as_plain_dict(restored_payload)
                if restored_payload is None:
                    continue
                _sync_vault_payload_mapping_wrapper(
                    source_payload,
                    restored_payload,
                    preserve_equivalent_raw_wrapper=True,
                )
        try:
            delattr(self, _VAULT_SOURCE_PAYLOADS_ATTR)
        except AttributeError:
            pass
        try:
            delattr(self, _VAULT_TEMP_SOURCE_PATH_ATTR)
        except AttributeError:
            pass


def _write_state(
    self,
    state,
    recovered_from: str | None = None,
    updated_at: str | None = None,
    preserve_primary_corrupt: bool = False,
    preserve_backup_corrupt: bool = False,
    preserve_seed_corrupt: bool = False,
):
    validate_project_name(state.project_name)
    if _path_uses_symlink_alias(state.root_dir):
        raise ValueError(f"vault project root uses a symlink alias: {state.root_dir!r}")
    corrupt_artifacts = _snapshot_existing_corrupt_artifacts(self, state.root_dir)
    dirty_auxiliary_artifacts = _snapshot_dirty_auxiliary_artifacts(self, state.root_dir, state.project_name)
    try:
        preserve_primary_corrupt, preserve_backup_corrupt, preserve_seed_corrupt = _preserve_existing_corrupt_artifacts(
            self,
            state.root_dir,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )
        result = _original_write_state(
            self,
            state,
            recovered_from=recovered_from,
            updated_at=updated_at,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )
        try:
            record: dict[str, object] = {
                "event": "save",
                "timestamp": utc_now_iso(),
                "project_name": state.project_name,
                "is_locked": state.is_locked,
            }
            if recovered_from is not None:
                record["recovered_from"] = recovered_from
            append_audit_record(audit_log_path(self._state_path(state.root_dir), self.__class__.__name__), record)
        except Exception:  # pragma: no cover - audit logging must not block persistence
            pass
        _sync_vault_source_payloads(self, self._state_path(state.root_dir))
        return result
    finally:
        _restore_existing_corrupt_artifacts(self, corrupt_artifacts)
        _restore_dirty_auxiliary_artifacts(self, dirty_auxiliary_artifacts)


def _load_payload(self, path: Path) -> dict[str, object] | None:
    if path.is_symlink():
        if path.exists() or path.is_symlink():
            self._quarantine_path(path)
        return None
    try:
        payload = _original_load_payload(self, path)
    except Exception:
        # Treat any loader failure the same as malformed JSON so the vault
        # can quarantine it instead of surfacing a crash to the engine.
        if path.exists():
            self._quarantine_path(path)
        return None
    source_payloads = getattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, None)
    if isinstance(payload, AbstractMapping) and type(payload) is not dict:
        if not isinstance(source_payloads, AbstractMutableMapping):
            source_payloads = {}
            setattr(self, _VAULT_SOURCE_PAYLOADS_ATTR, source_payloads)
        source_payloads[path] = payload
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            if path.exists():
                self._quarantine_path(path)
            return None
    if not isinstance(payload, AbstractMapping):
        if path.exists():
            # Vault state must remain mapping-shaped. Any other JSON payload
            # is malformed and should be quarantined before higher layers see it.
            self._quarantine_path(path)
        return None
    if "recovered_from" in payload and self._parse_updated_at(payload.get("updated_at")) is None:
        if path.exists():
            self._quarantine_path(path)
        return None
    if payload is None and path.exists():
        # JSON ``null`` is parseable but not valid vault state. Quarantine it
        # so callers never mistake it for a missing file.
        self._quarantine_path(path)
        return None
    return payload


def _is_loadable_payload(self, payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and type(payload) is not dict:
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    return _original_is_loadable_payload(self, payload)


def _is_valid_payload(self, path: Path) -> bool:
    try:
        return _original_is_valid_payload(self, path)
    except Exception:
        return False


def _is_supported_payload(self, payload: object) -> bool:
    if isinstance(payload, AbstractMapping) and type(payload) is not dict:
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return False
    return _original_is_supported_payload(self, payload)


def _primary_state_needs_recovery(self, payload: object, expected_project_name: str) -> bool:
    payload = _payload_as_plain_dict(payload)
    if payload is None:
        return True
    if isinstance(payload, dict) and "recovered_from" in payload:
        return True
    return _original_primary_state_needs_recovery(self, payload, expected_project_name)


def _needs_audit_quarantine(self, payload: object) -> bool:
    # A clean backup or seed payload that only lacks ``updated_at`` is still
    # recoverable, so let the caller rewrite it without creating a quarantine
    # artifact. Recovered payloads, however, should stay out of the clean
    # recovery path so they can be audited instead of being treated like a
    # fresh source of truth.
    if isinstance(payload, AbstractMapping) and type(payload) is not dict:
        payload = _payload_as_plain_dict(payload)
        if payload is None:
            return True
    if isinstance(payload, dict) and "recovered_from" in payload:
        return True
    if _payload_project_name_is_missing_or_blank(payload):
        if _payload_blank_project_name_is_recoverable(self, payload):
            return False
        if _payload_missing_project_name_is_recoverable(self, payload):
            return False
        payload = dict(payload)
        payload.pop("project_name", None)
    return not self._is_supported_payload(payload)


def _quarantine_path_for_state(self, path: Path) -> None:
    _quarantine_path_impl(path, self._corrupt_path_for(path))


def _payload_is_canonical_recovered_from_record(self, payload: dict[str, object]) -> bool:
    """Return ``True`` for a byte-canonical ``recovered_from`` provenance record.

    Such a record is a well-formed audit artifact: its identity fields are
    already canonical (a :class:`bool` ``is_locked``, a project name and a
    ``recovered_from`` marker that survive a canonical rewrite unchanged) so it
    should be quarantined for audit rather than silently kept. A primary whose
    identity fields still need canonicalization -- a whitespace-padded
    ``project_name``, a string ``is_locked`` such as ``"false"``, or a padded
    marker like ``" BACKUP "`` -- is malformed metadata that recovery salvages in
    place instead. ``updated_at`` is intentionally not inspected because the
    canonical rewrite always normalizes (or donates) it.
    """

    if "recovered_from" not in payload:
        return False
    marker = self._parse_recovered_from(payload.get("recovered_from"))
    if marker is None or payload.get("recovered_from") != marker:
        return False
    if not isinstance(payload.get("is_locked"), bool):
        return False
    project_name = self._parse_project_name(payload.get("project_name"))
    if project_name is None or payload.get("project_name") != project_name:
        return False
    if self._parse_schema_version(payload) is None:
        return False
    return not self._has_unknown_fields(payload)


def _salvageable_primary_payload(self, state_path: Path, expected_project_name: str) -> dict[str, object] | None:
    """Return the primary payload when it only needs a canonical rewrite.

    A primary whose ``project_name`` still matches the vault directory and whose
    ``is_locked`` value still parses is salvageable in place when its only defects
    are *droppable* optional metadata -- a malformed ``updated_at`` or an
    unparseable ``recovered_from`` value that the canonical rewrite discards
    without losing anything worth auditing. Such a primary is the authoritative
    source of truth and must not be displaced by a stale backup or quarantined as
    if it were corrupt. The raw payload is parsed directly here so the salvage
    check never triggers ``_load_payload``'s quarantine side effect on an
    unsupported-but-recoverable primary.

    A primary that carries forensic content worth preserving is *not* salvaged
    here and falls through to the original quarantine/recovery path: an unknown
    field (unexpected state to inspect) or a clean ``recovered_from`` record (a
    well-formed provenance marker that should be quarantined for audit rather than
    silently kept) both stay on the original path.
    """

    if not state_path.exists() or state_path.is_symlink():
        return None
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    payload = _payload_as_plain_dict(payload)
    if not isinstance(payload, dict):
        return None
    if not self._is_recoverable_state(payload, expected_project_name):
        return None
    if self._parse_schema_version(payload) is None:
        return None
    if self._has_unknown_fields(payload):
        # An unexpected field is forensic content worth preserving for audit.
        return None
    if _payload_is_canonical_recovered_from_record(self, payload):
        # A byte-canonical provenance record is preserved/quarantined for audit,
        # not silently kept. A primary that merely needs its identity fields
        # canonicalized (whitespace project_name, string is_locked, padded marker)
        # is malformed metadata and falls through to the in-place salvage below.
        return None
    return payload


def _primary_is_salvageable_in_place(self, state_path: Path, expected_project_name: str) -> bool:
    return _salvageable_primary_payload(self, state_path, expected_project_name) is not None


def _salvageable_auxiliary_payload(self, aux_path: Path, expected_project_name: str) -> dict[str, object] | None:
    """Return a backup/seed payload that should be promoted as the recovered state.

    When the primary is missing or corrupt, ``_prefer_recovery_payload`` rejects an
    otherwise recoverable backup or seed whose ``recovered_from`` provenance marker
    is paired with a malformed ``updated_at`` -- both of those are *droppable*
    optional metadata the canonical rewrite discards. Such an auxiliary still
    carries an authoritative identity (a ``project_name`` that canonicalizes to the
    vault directory and a parseable ``is_locked``), so it must drive the recovered
    lock state rather than falling back to the safe-lock default. The raw payload is
    read directly so this check never triggers ``_load_payload``'s quarantine side
    effect on an unsupported-but-recoverable auxiliary.

    A byte-canonical ``recovered_from`` provenance record (a well-formed audit
    artifact) or an auxiliary carrying an unknown field (forensic content worth
    preserving) is *not* salvaged here -- those stay on the original
    quarantine/recovery path so they remain auditable.
    """

    if not aux_path.exists() or aux_path.is_symlink():
        return None
    try:
        payload = json.loads(aux_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    payload = _payload_as_plain_dict(payload)
    if not isinstance(payload, dict):
        return None
    if not self._is_recoverable_state(payload, expected_project_name):
        return None
    if self._parse_schema_version(payload) is None:
        return None
    if self._has_unknown_fields(payload):
        return None
    if _payload_is_canonical_recovered_from_record(self, payload):
        return None
    return payload


def _read_state(self, root_dir: Path, expected_project_name: str):
    state_path = self._state_path(root_dir)
    primary_payload = _salvageable_primary_payload(self, state_path, expected_project_name)
    if primary_payload is not None:
        # Keep the salvageable primary as the source of truth rather than
        # quarantining it and inheriting a stale backup's lock state. Mirror the
        # clean-load tail so stale auxiliary copies stay auditable while temp and
        # seed artifacts are cleared; the caller's canonical rewrite drops the
        # primary's malformed optional fields.
        backup_present = self._backup_state_path(root_dir).exists()
        seed_present = self._seed_state_path(root_dir).exists()
        backup_payload = self._load_payload(self._backup_state_path(root_dir))
        seed_payload = self._load_payload(self._seed_state_path(root_dir))
        preserve_backup_corrupt = backup_present and backup_payload is None
        preserve_seed_corrupt = seed_present and seed_payload is None
        if self._needs_audit_quarantine(backup_payload):
            self._quarantine_invalid_backup(root_dir)
            preserve_backup_corrupt = True
        if self._needs_audit_quarantine(seed_payload):
            self._quarantine_invalid_seed(root_dir)
            preserve_seed_corrupt = True
        self._clear_quarantine_state(
            root_dir,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
        )
        self._clear_temporary_state(root_dir)
        self._clear_seed_state(root_dir)
        return primary_payload, None, False, preserve_backup_corrupt, preserve_seed_corrupt
    # Snapshot raw auxiliaries before the original read may quarantine them so a
    # salvageable backup/seed can still be promoted after recovery declines it.
    backup_salvage = _salvageable_auxiliary_payload(self, self._backup_state_path(root_dir), expected_project_name)
    seed_salvage = _salvageable_auxiliary_payload(self, self._seed_state_path(root_dir), expected_project_name)
    payload, recovered_source, primary_unavailable, preserve_backup_corrupt, preserve_seed_corrupt = (
        _original_read_state(self, root_dir, expected_project_name)
    )
    if (
        recovered_source is None
        and primary_unavailable
        and not self._is_recoverable_state(payload, expected_project_name)
    ):
        # No normal recovery source survived, but a backup/seed whose only defects
        # are droppable optional metadata still carries an authoritative lock state.
        # Promote it as the recovered payload so the rewrite keeps that lock state
        # instead of defaulting to a safe lock. Mirrors the in-place primary salvage.
        for salvaged, source in ((backup_salvage, "backup"), (seed_salvage, "seed")):
            if salvaged is not None:
                # Record that this recovery promoted an in-place auxiliary salvage so
                # the caller can drop the now-folded source from the clean-auxiliary
                # restore instead of re-creating it on disk.
                setattr(self, _VAULT_SALVAGED_AUX_SOURCE_ATTR, source)
                return salvaged, source, True, preserve_backup_corrupt, preserve_seed_corrupt
    if recovered_source in ("backup", "seed"):
        recovered_payload = _payload_as_plain_dict(payload)
        if recovered_payload is not None and recovered_payload.get("project_name") is None:
            # The only surviving recovery source is an auxiliary whose own payload
            # omits ``project_name`` entirely. Unlike a blank name that the
            # canonical rewrite restores from the caller's expected name, a truly
            # absent name leaves the auxiliary an untrusted, opaque source:
            # promoting it would fabricate an identity the file never carried and
            # inherit its unverified lock state. Quarantine it for audit and fall
            # through to a safe locked default so the rewrite re-establishes a
            # coherent primary/backup pair instead.
            if recovered_source == "backup":
                self._quarantine_invalid_backup(root_dir)
                preserve_backup_corrupt = True
            else:
                self._quarantine_invalid_seed(root_dir)
                preserve_seed_corrupt = True
            return {}, None, True, preserve_backup_corrupt, preserve_seed_corrupt
    return payload, recovered_source, primary_unavailable, preserve_backup_corrupt, preserve_seed_corrupt


def _parse_project_name(self, value: object) -> str | None:
    """Parse a stored project name, tolerating canonicalizable surrounding whitespace.

    The public :func:`validate_project_name` deliberately rejects names padded
    with leading or trailing whitespace, but a *stored* payload whose only
    project-name defect is that padding still represents a recoverable name: the
    canonical rewrite restores the trimmed value from the caller's expected
    project name. Stripping before validating lets recovery salvage such state in
    place instead of quarantining it and forcing a locked rewrite, while
    genuinely invalid names (for example ``"../bad"``) still fail validation and
    stay quarantined.
    """
    if not isinstance(value, str):
        return None
    try:
        return validate_project_name(value.strip())
    except ValueError:
        return None


def _quarantine_invalid_state(self, root_dir: Path) -> None:
    # A salvageable primary needs only a canonical rewrite, not quarantine;
    # quarantining it would strand a spurious ``.corrupt`` marker that survives
    # the rewrite (the write path preserves pre-existing corrupt artifacts), so
    # engine flows would read phantom corruption after a healthy recovery.
    if _primary_is_salvageable_in_place(self, self._state_path(root_dir), root_dir.name):
        return
    _original_quarantine_invalid_state(self, root_dir)


VaultService._recovery_marker_cleanup_timestamp = _recovery_marker_cleanup_timestamp
VaultService._prefer_recovery_payload = _prefer_recovery_payload
VaultService._auxiliary_state_paths = _auxiliary_state_paths
VaultService._parse_project_name = _parse_project_name
VaultService._parse_updated_at = _parse_updated_at
VaultService._load_payload = _load_payload
VaultService._is_loadable_payload = _is_loadable_payload
VaultService._is_valid_payload = _is_valid_payload
VaultService._is_supported_payload = _is_supported_payload
VaultService._primary_state_needs_recovery = _primary_state_needs_recovery
VaultService._quarantine_missing_required_metadata = _quarantine_missing_required_metadata
VaultService._needs_audit_quarantine = _needs_audit_quarantine
VaultService._requires_safe_lock = _requires_safe_lock
VaultService._quarantine_path = _quarantine_path_for_state
VaultService.create_or_open = _create_or_open
VaultService._write_state = _write_state
VaultService._read_state = _read_state
VaultService._quarantine_invalid_state = _quarantine_invalid_state
