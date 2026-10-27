from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VERSION = 1
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


def _derive(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValueError("Vault password cannot be empty")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=KEY_SIZE, salt=salt, iterations=600_000)
    return kdf.derive(password.encode("utf-8"))


def create_vault(path: str | Path, password: str) -> None:
    p = Path(path)
    if p.exists():
        raise FileExistsError(p)
    payload = {"version": VERSION, "keys": {}}
    _write(p, password, payload)


def _write(path: Path, password: str, payload: dict) -> None:
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = _derive(password, salt)
    plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, b"crypto-auto-vault-v1")
    envelope = {"version": VERSION, "salt": base64.b64encode(salt).decode(), "nonce": base64.b64encode(nonce).decode(), "ciphertext": base64.b64encode(ciphertext).decode()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _read(path: Path, password: str) -> dict:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if envelope.get("version") != VERSION:
        raise ValueError("Unsupported vault version")
    salt = base64.b64decode(envelope["salt"])
    nonce = base64.b64decode(envelope["nonce"])
    ciphertext = base64.b64decode(envelope["ciphertext"])
    key = _derive(password, salt)
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, b"crypto-auto-vault-v1")
    return json.loads(plaintext)


def put_key(path: str | Path, password: str, name: str, key_type: str, value: bytes) -> None:
    p = Path(path)
    data = _read(p, password) if p.exists() else {"version": VERSION, "keys": {}}
    data.setdefault("keys", {})[name] = {"type": key_type, "value": base64.b64encode(value).decode()}
    _write(p, password, data)


def list_keys(path: str | Path, password: str) -> list[dict[str, str]]:
    data = _read(Path(path), password)
    return [{"name": name, "type": item["type"]} for name, item in data.get("keys", {}).items()]


def get_key(path: str | Path, password: str, name: str) -> tuple[str, bytes]:
    data = _read(Path(path), password)
    item = data.get("keys", {}).get(name)
    if not item:
        raise KeyError(name)
    return item["type"], base64.b64decode(item["value"])


def delete_key(path: str | Path, password: str, name: str) -> None:
    p = Path(path)
    data = _read(p, password)
    if name not in data.get("keys", {}):
        raise KeyError(name)
    del data["keys"][name]
    _write(p, password, data)
