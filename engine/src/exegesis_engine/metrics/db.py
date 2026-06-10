from __future__ import annotations

import secrets
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator

from exegesis_engine.metrics.crypto import decrypt_bytes, encrypt_bytes
from exegesis_engine.metrics.schema import WEEKLY_COUNTER_FIELDS

_DB_FILENAME = "metrics_v1.db.enc"
_KEY_FILENAME = "metrics_v1.key"


@dataclass(frozen=True)
class MetricsInstallRecord:
    install_created_at: str
    t_first_export_hours: int | None
    t_first_accept_hours: int | None
    cohort_code: str | None
    install_uuid: str | None
    include_install_uuid_default: bool


class MetricsDB:
    def __init__(self, app_data_dir: Path) -> None:
        self._dir = app_data_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._dir / _DB_FILENAME
        self._key_path = self._dir / _KEY_FILENAME
        self._key = self._load_or_create_key()

    def list_user_tables(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            ).fetchall()
        return [str(row[0]) for row in rows]

    def get_weeks(self, *, limit: int | None = None, descending: bool = False) -> list[dict[str, int | str]]:
        order = "DESC" if descending else "ASC"
        select_columns = ", ".join(["week_start", *WEEKLY_COUNTER_FIELDS])
        query = f"SELECT {select_columns} FROM metrics_weekly ORDER BY week_start {order}"
        params: tuple[object, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        keys = ["week_start", *WEEKLY_COUNTER_FIELDS]
        result: list[dict[str, int | str]] = []
        for row in rows:
            entry: dict[str, int | str] = {}
            for idx, key in enumerate(keys):
                entry[key] = row[idx]
            result.append(entry)
        return result

    def increment_week(self, *, week_start: str, increments: dict[str, int], set_waw: bool = False) -> None:
        for key, value in increments.items():
            if key not in WEEKLY_COUNTER_FIELDS:
                raise ValueError(f"unknown weekly counter: {key}")
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"increment for {key} must be non-negative integer")

        with self._connect() as conn:
            self._ensure_week_row(conn, week_start)
            if increments:
                for key, value in increments.items():
                    if value == 0:
                        continue
                    conn.execute(
                        f"UPDATE metrics_weekly SET {key} = {key} + ? WHERE week_start = ?",
                        (value, week_start),
                    )
            if set_waw:
                conn.execute("UPDATE metrics_weekly SET waw = 1 WHERE week_start = ?", (week_start,))

    def get_install(self) -> MetricsInstallRecord:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT install_created_at, t_first_export_hours, t_first_accept_hours, "
                "cohort_code, install_uuid, include_install_uuid_default "
                "FROM metrics_install WHERE id = 1"
            ).fetchone()
        if row is None:
            raise RuntimeError("metrics_install row missing")
        return MetricsInstallRecord(
            install_created_at=str(row[0]),
            t_first_export_hours=self._as_opt_int(row[1]),
            t_first_accept_hours=self._as_opt_int(row[2]),
            cohort_code=self._as_opt_str(row[3]),
            install_uuid=self._as_opt_str(row[4]),
            include_install_uuid_default=bool(int(row[5])),
        )

    def set_first_export_hours_if_unset(self, hours_since_install: int) -> None:
        self._set_first_hours_if_unset("t_first_export_hours", hours_since_install)

    def set_first_accept_hours_if_unset(self, hours_since_install: int) -> None:
        self._set_first_hours_if_unset("t_first_accept_hours", hours_since_install)

    def update_install_metadata(
        self,
        *,
        cohort_code: str | None = None,
        install_uuid: str | None = None,
        include_install_uuid_default: bool | None = None,
    ) -> None:
        sets: list[str] = []
        params: list[object] = []
        if cohort_code is not None:
            sets.append("cohort_code = ?")
            params.append(cohort_code)
        if install_uuid is not None:
            sets.append("install_uuid = ?")
            params.append(install_uuid)
        if include_install_uuid_default is not None:
            sets.append("include_install_uuid_default = ?")
            params.append(1 if include_install_uuid_default else 0)
        if not sets:
            return
        with self._connect() as conn:
            conn.execute(f"UPDATE metrics_install SET {', '.join(sets)} WHERE id = 1", tuple(params))

    def hours_since_install(self, *, now: datetime | None = None) -> int:
        install = self.get_install()
        created = datetime.fromisoformat(install.install_created_at)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        current = now if now is not None else datetime.now(UTC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=UTC)
        delta = current - created
        return max(0, int(delta.total_seconds() // 3600))

    def _set_first_hours_if_unset(self, column: str, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{column} must be non-negative integer")
        with self._connect() as conn:
            conn.execute(
                f"UPDATE metrics_install SET {column} = ? WHERE id = 1 AND {column} IS NULL",
                (value,),
            )

    def _load_or_create_key(self) -> bytes:
        if self._key_path.exists():
            raw = self._key_path.read_bytes()
            if len(raw) < 32:
                raise ValueError("metrics key file is invalid")
            return raw[:32]
        key = secrets.token_bytes(32)
        self._key_path.write_bytes(key)
        return key

    def _ensure_week_row(self, conn: sqlite3.Connection, week_start: str) -> None:
        conn.execute("INSERT OR IGNORE INTO metrics_weekly(week_start) VALUES (?)", (week_start,))

    def _initialize_schema(self, conn: sqlite3.Connection) -> None:
        weekly_cols = ",\n  ".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in WEEKLY_COUNTER_FIELDS)
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS metrics_weekly (
              week_start TEXT PRIMARY KEY,
              {weekly_cols}
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics_install (
              id INTEGER PRIMARY KEY CHECK (id = 1),
              install_created_at TEXT NOT NULL,
              t_first_export_hours INTEGER,
              t_first_accept_hours INTEGER,
              cohort_code TEXT,
              install_uuid TEXT,
              include_install_uuid_default INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        created_at = datetime.now(UTC).isoformat()
        conn.execute(
            """
            INSERT OR IGNORE INTO metrics_install(
              id, install_created_at, t_first_export_hours, t_first_accept_hours,
              cohort_code, install_uuid, include_install_uuid_default
            ) VALUES (1, ?, NULL, NULL, NULL, NULL, 0)
            """,
            (created_at,),
        )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        with NamedTemporaryFile(prefix="metrics_", suffix=".sqlite3", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            if self._db_path.exists():
                encrypted = self._db_path.read_bytes()
                plaintext = decrypt_bytes(encrypted, self._key)
                tmp_path.write_bytes(plaintext)
            conn = sqlite3.connect(str(tmp_path))
            try:
                self._initialize_schema(conn)
                yield conn
                conn.commit()
            finally:
                conn.close()
            encrypted = encrypt_bytes(tmp_path.read_bytes(), self._key)
            out_tmp = self._db_path.with_suffix(".tmp")
            out_tmp.write_bytes(encrypted)
            out_tmp.replace(self._db_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    @staticmethod
    def _as_opt_int(value: object) -> int | None:
        if value is None:
            return None
        return int(value)

    @staticmethod
    def _as_opt_str(value: object) -> str | None:
        if value is None:
            return None
        return str(value)
