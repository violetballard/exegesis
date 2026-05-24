from __future__ import annotations

import json
import re
from datetime import datetime, timezone

UTC = timezone.utc
from dataclasses import dataclass
from pathlib import Path

from src.qual.config import validate_project_name

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
        (
            raw_state,
            recovered_source,
            primary_unavailable,
            preserve_backup_corrupt,
            preserve_seed_corrupt,
            preserve_temporary_corrupt,
        ) = self._read_state(
            project_root,
            safe_project_name,
        )
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
                preserve_temporary_corrupt=preserve_temporary_corrupt,
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
                preserve_temporary_corrupt=preserve_temporary_corrupt,
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
    ) -> tuple[dict[str, object], str | None, bool, bool, bool, bool]:
        state_path = self._state_path(root_dir)
        primary_missing = not state_path.exists()
        backup_present = self._backup_state_path(root_dir).exists()
        seed_present = self._seed_state_path(root_dir).exists()
        primary_payload, _ = self._load_payload(state_path)
        tmp_payload, tmp_quarantined = self._load_payload(self._tmp_state_path(root_dir))
        backup_tmp_payload, backup_tmp_quarantined = self._load_payload(self._backup_tmp_state_path(root_dir))
        backup_payload, _ = self._load_payload(self._backup_state_path(root_dir))
        seed_tmp_payload, seed_tmp_quarantined = self._load_payload(self._seed_tmp_state_path(root_dir))
        seed_payload, _ = self._load_payload(self._seed_state_path(root_dir))
        preserve_temporary_corrupt = tmp_quarantined or backup_tmp_quarantined or seed_tmp_quarantined
        tmp_missing_required_metadata = self._quarantine_missing_required_metadata(
            self._tmp_state_path(root_dir),
            tmp_payload,
        )
        backup_tmp_missing_required_metadata = self._quarantine_missing_required_metadata(
            self._backup_tmp_state_path(root_dir),
            backup_tmp_payload,
        )
        preserve_backup_corrupt = self._quarantine_missing_required_metadata(
            self._backup_state_path(root_dir),
            backup_payload,
        )
        seed_tmp_missing_required_metadata = self._quarantine_missing_required_metadata(
            self._seed_tmp_state_path(root_dir),
            seed_tmp_payload,
        )
        preserve_seed_corrupt = self._quarantine_missing_required_metadata(
            self._seed_state_path(root_dir),
            seed_payload,
        )
        preserve_temporary_corrupt = (
            preserve_temporary_corrupt
            or tmp_missing_required_metadata
            or backup_tmp_missing_required_metadata
            or seed_tmp_missing_required_metadata
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
                preserve_temporary_corrupt=preserve_temporary_corrupt,
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
                        preserve_temporary_corrupt=preserve_temporary_corrupt,
                    )
                    self._clear_temporary_state(root_dir)
                    return (
                        {},
                        None,
                        primary_payload is None,
                        preserve_backup_corrupt,
                        preserve_seed_corrupt,
                        preserve_temporary_corrupt,
                    )
        if not isinstance(payload, dict):
            return {}, None, primary_payload is None, preserve_backup_corrupt, preserve_seed_corrupt, preserve_temporary_corrupt
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
        return (
            payload,
            recovered_source,
            primary_unavailable,
            preserve_backup_corrupt,
            preserve_seed_corrupt,
            preserve_temporary_corrupt,
        )

    def _write_state(
        self,
        state: VaultState,
        recovered_from: str | None = None,
        updated_at: str | None = None,
        preserve_primary_corrupt: bool = False,
        preserve_backup_corrupt: bool = False,
        preserve_seed_corrupt: bool = False,
        preserve_temporary_corrupt: bool = False,
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
            preserve_temporary_corrupt=preserve_temporary_corrupt,
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
        preserve_temporary_corrupt: bool = False,
    ) -> None:
        if not preserve_primary_corrupt:
            self._unlink_if_exists(self._corrupt_state_path(root_dir))
        if not preserve_backup_corrupt:
            self._unlink_if_exists(self._corrupt_path_for(self._backup_state_path(root_dir)))
        if not preserve_seed_corrupt:
            self._unlink_if_exists(self._corrupt_path_for(self._seed_state_path(root_dir)))
        if not preserve_temporary_corrupt:
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
        preserve_temporary_corrupt: bool = False,
    ) -> None:
        self._clear_quarantine_state(
            root_dir,
            preserve_primary_corrupt=preserve_primary_corrupt,
            preserve_backup_corrupt=preserve_backup_corrupt,
            preserve_seed_corrupt=preserve_seed_corrupt,
            preserve_temporary_corrupt=preserve_temporary_corrupt,
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

    def _load_payload(self, path: Path) -> tuple[dict[str, object] | None, bool]:
        if not path.exists():
            return None, False
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
            return None, True
        if not self._is_loadable_payload(payload):
            if path.name == _STATE_FILE:
                self._quarantine_invalid_state(path.parent)
            elif path.suffix == ".tmp":
                self._quarantine_path(path)
            elif path == self._backup_state_path(path.parent):
                self._quarantine_invalid_backup(path.parent)
            elif path == self._seed_state_path(path.parent):
                self._quarantine_invalid_seed(path.parent)
            return None, True
        return payload, False

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
