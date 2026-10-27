from __future__ import annotations

import base64
import hashlib
import hmac
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"CRYPTOAUTO1"
NONCE_SIZE = 12
KEY_SIZE = 32


def generate_aes_key() -> bytes:
    return os.urandom(KEY_SIZE)


def encrypt_bytes(key: bytes, plaintext: bytes, *, associated_data: bytes | None = None) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError("AES-256 key must be exactly 32 bytes")
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, associated_data)
    return MAGIC + nonce + ciphertext


def decrypt_bytes(key: bytes, payload: bytes, *, associated_data: bytes | None = None) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError("AES-256 key must be exactly 32 bytes")
    if not payload.startswith(MAGIC) or len(payload) <= len(MAGIC) + NONCE_SIZE:
        raise ValueError("Invalid cryptographic container")
    nonce_start = len(MAGIC)
    nonce = payload[nonce_start:nonce_start + NONCE_SIZE]
    ciphertext = payload[nonce_start + NONCE_SIZE:]
    return AESGCM(key).decrypt(nonce, ciphertext, associated_data)


def hash_file(path: str | Path, algorithm: str = "sha256", chunk_size: int = 1024 * 1024) -> str:
    algorithm = algorithm.lower().replace("-", "")
    if algorithm not in {"sha256", "sha512"}:
        raise ValueError("Supported hashes: sha256, sha512")
    digest = hashlib.new(algorithm)
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_hmac_key() -> bytes:
    return os.urandom(32)


def create_hmac(key: bytes, data: bytes) -> str:
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def verify_hmac(key: bytes, data: bytes, expected_hex: str) -> bool:
    return hmac.compare_digest(create_hmac(key, data), expected_hex.lower())


def generate_ed25519_keys() -> tuple[bytes, bytes]:
    private = ed25519.Ed25519PrivateKey.generate()
    public = private.public_key()
    private_raw = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    public_raw = public.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return private_raw, public_raw


def sign_bytes(private_raw: bytes, data: bytes) -> bytes:
    if len(private_raw) != 32:
        raise ValueError("Ed25519 private key must be 32 bytes")
    return ed25519.Ed25519PrivateKey.from_private_bytes(private_raw).sign(data)


def verify_signature(public_raw: bytes, data: bytes, signature: bytes) -> bool:
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(public_raw).verify(signature, data)
        return True
    except Exception:
        return False


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
