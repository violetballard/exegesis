from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from src.qual.metrics.crypto import decrypt_bytes, encrypt_bytes


@dataclass
class VaultStore:
    root: Path
    namespace: str
    key_filename: str

    def __post_init__(self) -> None:
        self._ns = self.root / self.namespace
        self._ns.mkdir(parents=True, exist_ok=True)
        self._key_path = self._ns / self.key_filename
        self._key = self._load_or_create_key()

    @property
    def path(self) -> Path:
        return self._ns

    def read_json(self, rel_path: str, *, default: object) -> object:
        path = self._ns / rel_path
        if not path.exists():
            return default
        payload = decrypt_bytes(path.read_bytes(), self._key)
        try:
            return json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError:
            return default

    def write_json(self, rel_path: str, payload: object) -> None:
        path = self._ns / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        path.write_bytes(encrypt_bytes(plaintext, self._key))

    def read_blob(self, rel_path: str) -> bytes:
        path = self._ns / rel_path
        return decrypt_bytes(path.read_bytes(), self._key)

    def write_blob(self, rel_path: str, payload: bytes) -> None:
        path = self._ns / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypt_bytes(payload, self._key))

    def _load_or_create_key(self) -> bytes:
        if self._key_path.exists():
            raw = self._key_path.read_bytes()
            if len(raw) < 32:
                raise ValueError("vault store key file is invalid")
            return raw[:32]
        raw = (uuid.uuid4().bytes + uuid.uuid4().bytes)[:32]
        self._key_path.write_bytes(raw)
        return raw
