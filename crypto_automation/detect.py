from __future__ import annotations

import base64
import binascii
import json
import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    name: str
    confidence: float
    category: str
    reason: str
    decoded_preview: str = ""


def _printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    return sum(b in (9, 10, 13) or 32 <= b <= 126 for b in data) / len(data)


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [data.count(i) for i in range(256)]
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def _preview(data: bytes) -> str:
    return data[:180].decode("utf-8", errors="replace")


def _try(name: str, category: str, confidence: float, reason: str, fn, sample: str) -> Detection | None:
    try:
        decoded = fn(sample)
        if not decoded:
            return None
        return Detection(name, min(confidence, 1.0), category, reason, _preview(decoded))
    except Exception:
        return None


def detect_sample(sample: str) -> list[Detection]:
    text = sample.strip()
    results: list[Detection] = []
    if not text:
        return results

    # URL encoding
    if re.search(r"%[0-9A-Fa-f]{2}", text):
        from urllib.parse import unquote_to_bytes
        decoded = unquote_to_bytes(text)
        results.append(Detection("URL percent-encoding", "0.95" if False else 0.95, "encoding", "Contains valid percent-encoded byte sequences.", _preview(decoded)))

    # Hex: avoid calling ordinary short decimal/text strings hex.
    compact = re.sub(r"\s+", "", text)
    if len(compact) >= 4 and len(compact) % 2 == 0 and re.fullmatch(r"[0-9A-Fa-f]+", compact):
        try:
            raw = bytes.fromhex(compact)
            if _printable_ratio(raw) > 0.55:
                results.append(Detection("Hex / hexadecimal", 0.98, "encoding", "Even-length hexadecimal data decodes to mostly printable bytes.", _preview(raw)))
        except ValueError:
            pass

    # Base64 and Base64URL.
    if len(compact) >= 8 and re.fullmatch(r"[A-Za-z0-9+/]*={0,2}", compact):
        padded = compact + "=" * (-len(compact) % 4)
        try:
            raw = base64.b64decode(padded, validate=True)
            score = 0.92 if _printable_ratio(raw) > 0.6 else 0.78
            results.append(Detection("Base64", score, "encoding", "Alphabet and padding match Base64 and decoding succeeded.", _preview(raw)))
        except Exception:
            pass

    if len(compact) >= 8 and re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", compact) and ("-" in compact or "_" in compact):
        try:
            raw = base64.urlsafe_b64decode(compact + "=" * (-len(compact) % 4))
            results.append(Detection("Base64URL", 0.94, "encoding", "URL-safe Base64 alphabet detected and decoding succeeded.", _preview(raw)))
        except Exception:
            pass

    # Base32
    if len(compact) >= 8 and re.fullmatch(r"[A-Z2-7]+=*", compact, re.I):
        try:
            raw = base64.b32decode(compact.upper() + "=" * (-len(compact) % 8))
            results.append(Detection("Base32", 0.88, "encoding", "Characters are compatible with the RFC 4648 Base32 alphabet.", _preview(raw)))
        except Exception:
            pass

    # Binary
    binary = re.sub(r"\s+", "", text)
    if len(binary) >= 8 and len(binary) % 8 == 0 and re.fullmatch(r"[01]+", binary):
        try:
            raw = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
            results.append(Detection("Binary / bit string", 0.96, "encoding", "Only binary digits are present and length is byte-aligned.", _preview(raw)))
        except Exception:
            pass

    # JWT is structurally recognizable; payload decoding is intentionally read-only.
    parts = text.split(".")
    if len(parts) == 3 and all(re.fullmatch(r"[A-Za-z0-9_-]+", p) for p in parts):
        try:
            payload = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
            json.loads(payload)
            results.append(Detection("JWT", 0.99, "token", "Three URL-safe segments with a JSON-decoded payload were detected.", _preview(payload)))
        except Exception:
            results.append(Detection("JWT-like token", 0.82, "token", "Three URL-safe dot-separated segments were detected."))

    # Plain text / UTF-8 is a fallback, not an encryption claim.
    raw = text.encode("utf-8")
    results.append(Detection("UTF-8 / plain text", 0.70, "text", "The sample is valid UTF-8 text; this does not imply that it is encrypted." , text[:180]))

    # Useful diagnostic: high entropy can indicate compressed/encrypted/random data, but cannot identify an algorithm.
    entropy = _entropy(raw)
    if len(raw) >= 32 and entropy >= 7.2:
        results.append(Detection("High-entropy binary/text", 0.74, "diagnostic", f"Observed Shannon entropy is approximately {entropy:.2f} bits/byte; this can be consistent with encrypted or compressed data."))

    # De-duplicate and rank.
    unique: dict[str, Detection] = {}
    for item in results:
        old = unique.get(item.name)
        if old is None or item.confidence > old.confidence:
            unique[item.name] = item
    return sorted(unique.values(), key=lambda x: x.confidence, reverse=True)
