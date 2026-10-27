from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .crypto import (
    create_hmac, decrypt_bytes, encrypt_bytes, generate_aes_key,
    generate_ed25519_keys, generate_hmac_key, hash_file, sign_bytes,
    verify_hmac, verify_signature,
)


def _write_private(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(prog="crypto-auto", description="Automate common cryptographic workflows safely.")
    sub = parser.add_subparsers(dest="command", required=True)

    keygen = sub.add_parser("keygen")
    keygen_sub = keygen.add_subparsers(dest="kind", required=True)
    aes = keygen_sub.add_parser("aes")
    aes.add_argument("--output", required=True, type=Path)
    hmk = keygen_sub.add_parser("hmac")
    hmk.add_argument("--output", required=True, type=Path)
    ed = keygen_sub.add_parser("ed25519")
    ed.add_argument("--private-key", required=True, type=Path)
    ed.add_argument("--public-key", required=True, type=Path)

    enc = sub.add_parser("encrypt")
    enc.add_argument("key", type=Path); enc.add_argument("input", type=Path); enc.add_argument("output", type=Path)
    dec = sub.add_parser("decrypt")
    dec.add_argument("key", type=Path); dec.add_argument("input", type=Path); dec.add_argument("output", type=Path)
    hs = sub.add_parser("hash")
    hs.add_argument("input", type=Path); hs.add_argument("--algorithm", default="sha256", choices=["sha256", "sha512"]); hs.add_argument("--output", type=Path)
    hm = sub.add_parser("hmac")
    hm.add_argument("key", type=Path); hm.add_argument("input", type=Path); hm.add_argument("--verify", type=str)
    sg = sub.add_parser("sign")
    sg.add_argument("key", type=Path); sg.add_argument("input", type=Path); sg.add_argument("output", type=Path)
    vf = sub.add_parser("verify")
    vf.add_argument("key", type=Path); vf.add_argument("input", type=Path); vf.add_argument("signature", type=Path)

    args = parser.parse_args()

    if args.command == "keygen":
        if args.kind == "aes": _write_private(args.output, generate_aes_key())
        elif args.kind == "hmac": _write_private(args.output, generate_hmac_key())
        else:
            private, public = generate_ed25519_keys(); _write_private(args.private_key, private); args.public_key.write_bytes(public)
        print("key generated")
    elif args.command == "encrypt":
        args.output.write_bytes(encrypt_bytes(args.key.read_bytes(), args.input.read_bytes()))
        print(f"encrypted: {args.output}")
    elif args.command == "decrypt":
        args.output.write_bytes(decrypt_bytes(args.key.read_bytes(), args.input.read_bytes()))
        print(f"decrypted: {args.output}")
    elif args.command == "hash":
        value = hash_file(args.input, args.algorithm)
        if args.output: args.output.write_text(value + "\n", encoding="utf-8")
        else: print(value)
    elif args.command == "hmac":
        value = create_hmac(args.key.read_bytes(), args.input.read_bytes())
        if args.verify: print("valid" if verify_hmac(args.key.read_bytes(), args.input.read_bytes(), args.verify) else "invalid")
        else: print(value)
    elif args.command == "sign":
        args.output.write_bytes(sign_bytes(args.key.read_bytes(), args.input.read_bytes())); print(f"signature: {args.output}")
    elif args.command == "verify":
        print("valid" if verify_signature(args.key.read_bytes(), args.input.read_bytes(), args.signature.read_bytes()) else "invalid")
