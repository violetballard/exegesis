from __future__ import annotations

import hashlib
import hmac
import secrets

_VERSION = b"\x01"
_NONCE_BYTES = 16
_MAC_BYTES = 32


def encrypt_bytes(plaintext: bytes, key: bytes) -> bytes:
    nonce = secrets.token_bytes(_NONCE_BYTES)
    ciphertext = _xor_stream(plaintext, key=key, nonce=nonce)
    body = _VERSION + nonce + ciphertext
    mac = hmac.new(key, body, digestmod=hashlib.sha256).digest()
    return body + mac


def decrypt_bytes(payload: bytes, key: bytes) -> bytes:
    min_len = 1 + _NONCE_BYTES + _MAC_BYTES
    if len(payload) < min_len:
        raise ValueError("invalid encrypted payload")
    version = payload[:1]
    if version != _VERSION:
        raise ValueError("unsupported encrypted payload version")
    nonce = payload[1 : 1 + _NONCE_BYTES]
    ciphertext = payload[1 + _NONCE_BYTES : -_MAC_BYTES]
    body = payload[:-_MAC_BYTES]
    expected_mac = hmac.new(key, body, digestmod=hashlib.sha256).digest()
    actual_mac = payload[-_MAC_BYTES:]
    if not hmac.compare_digest(expected_mac, actual_mac):
        raise ValueError("encrypted payload integrity check failed")
    return _xor_stream(ciphertext, key=key, nonce=nonce)


def _xor_stream(data: bytes, *, key: bytes, nonce: bytes) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < len(data):
        seed = nonce + counter.to_bytes(8, "big")
        block = hashlib.sha256(key + seed).digest()
        out.extend(block)
        counter += 1
    return bytes(a ^ b for a, b in zip(data, out, strict=False))
