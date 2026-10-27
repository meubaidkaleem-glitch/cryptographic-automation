from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import secrets
import zipfile
from pathlib import Path

import streamlit as st

from crypto_automation.crypto import (
    decrypt_bytes,
    encrypt_bytes,
    generate_aes_key,
    generate_ed25519_keys,
    generate_hmac_key,
    sign_bytes,
    verify_hmac,
    verify_signature,
)
from crypto_automation.detect import detect_sample

st.set_page_config(page_title="Cryptographic Automation", page_icon="CA", layout="wide")


def download_bytes(label: str, data: bytes, filename: str, mime: str = "application/octet-stream") -> None:
    st.download_button(label, data=data, file_name=filename, mime=mime, use_container_width=True)


def hash_bytes(data: bytes, algorithm: str) -> str:
    return hashlib.new(algorithm.replace("-", "").lower(), data).hexdigest()


def init_state() -> None:
    st.session_state.setdefault("jobs", [])
    st.session_state.setdefault("audit", [])


def audit(action: str, detail: str) -> None:
    st.session_state.audit.insert(0, {"action": action, "detail": detail})


init_state()
st.title("Cryptographic Automation")
st.caption("A local-first workbench for encoding analysis, encryption, integrity, signatures, keys, batch workflows, and audit history.")

with st.sidebar:
    st.header("Workflow")
    st.markdown("1. **Analyze** a sample\n2. **Transform** data or files\n3. **Protect** with encryption/signatures\n4. **Verify** integrity\n5. **Automate** repeatable jobs\n6. **Review** the audit trail")
    st.divider()
    st.info("Encoding detection is heuristic. It can identify common encodings such as Base64, Base32, hex, binary, URL encoding and JWT-like structures, but it cannot reliably determine an unknown encryption algorithm from ciphertext alone.")

# Dashboard

tabs = st.tabs(["Dashboard", "Encoding Analyzer", "Encrypt / Decrypt", "Hash & HMAC", "Sign & Verify", "Key Lab", "Batch Jobs", "Audit"])

with tabs[0]:
    st.subheader("Cryptographic automation workspace")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jobs", len(st.session_state.jobs))
    c2.metric("Audit events", len(st.session_state.audit))
    c3.metric("Crypto primitives", "AES-GCM + Ed25519")
    c4.metric("Hashing", "SHA-256 / SHA-512")
    st.markdown("### Application scope")
    st.write("This application is designed around a complete local workflow rather than a single encrypt/decrypt function. Each tab is independently useful and the same session can move from detection to transformation, protection, verification, automation and reporting.")
    st.markdown("#### Security boundaries")
    st.write("The app uses established primitives from Python's `cryptography` package and does not implement custom cryptographic algorithms. Detection results are evidence-based guesses, not proof of an encryption scheme.")

with tabs[1]:
    st.subheader("Automatic Encoding & Sample Analyzer")
    st.write("Paste a sample below. The analyzer tests multiple common representations and ranks the successful interpretations.")
    sample = st.text_area("Sample", height=220, placeholder="Paste Base64, Base32, hex, binary, URL-encoded text, a JWT-like token, or ordinary text...")
    if st.button("Analyze sample", type="primary", use_container_width=True):
        if not sample.strip():
            st.warning("Provide a sample first.")
        else:
            results = detect_sample(sample)
            for result in results[:8]:
                with st.container(border=True):
                    left, right = st.columns([1, 4])
                    left.metric(result.name, f"{result.confidence:.0%}")
                    right.write(f"**Category:** {result.category}  ")
                    right.write(result.reason)
                    if result.decoded_preview:
                        right.code(result.decoded_preview, language="text")
            audit("sample_analysis", f"Analyzed {len(sample)} characters; {len(results)} interpretations returned.")

with tabs[2]:
    st.subheader("AES-256-GCM File/Data Protection")
    mode = st.radio("Operation", ["Encrypt", "Decrypt"], horizontal=True)
    uploaded = st.file_uploader("Input file", key="crypto_file")
    key_text = st.text_input("AES key (hex)", type="password", help="Leave blank during encryption to generate a new 32-byte key.")
    if mode == "Encrypt":
        if st.button("Encrypt", type="primary") and uploaded:
            key = bytes.fromhex(key_text) if key_text else generate_aes_key()
            if len(key) != 32:
                st.error("AES-256 requires exactly 32 bytes (64 hex characters).")
            else:
                encrypted = encrypt_bytes(key, uploaded.getvalue())
                download_bytes("Download encrypted container", encrypted, uploaded.name + ".enc")
                st.success("Encryption completed with AES-256-GCM.")
                if not key_text:
                    st.warning("Save this key securely. It is required for decryption.")
                    st.code(key.hex())
                audit("encrypt", uploaded.name)
    else:
        if st.button("Decrypt", type="primary") and uploaded:
            try:
                key = bytes.fromhex(key_text)
                plaintext = decrypt_bytes(key, uploaded.getvalue())
                download_bytes("Download decrypted file", plaintext, uploaded.name.removesuffix(".enc") + ".recovered")
                st.success("Authentication and decryption succeeded.")
                audit("decrypt", uploaded.name)
            except Exception as exc:
                st.error(f"Decryption failed or authentication did not pass: {exc}")

with tabs[3]:
    st.subheader("Hash & HMAC")
    data_file = st.file_uploader("File", key="hash_file")
    algorithm = st.selectbox("Hash algorithm", ["sha256", "sha512"])
    if data_file:
        digest = hash_bytes(data_file.getvalue(), algorithm)
        st.code(digest)
        if st.button("Record hash", use_container_width=True):
            audit("hash", f"{algorithm.upper()} of {data_file.name}")
    st.divider()
    st.markdown("### HMAC-SHA256")
    hmac_file = st.file_uploader("HMAC input", key="hmac_file")
    hmac_key = st.text_input("HMAC key (hex)", type="password")
    if hmac_file:
        if not hmac_key:
            generated = generate_hmac_key()
            st.code(generated.hex())
            st.caption("Generated key — store it securely before leaving this session.")
        else:
            try:
                key = bytes.fromhex(hmac_key)
                tag = hmac.new(key, hmac_file.getvalue(), hashlib.sha256).hexdigest()
                st.code(tag)
                st.caption("HMAC-SHA256 authentication tag")
            except ValueError:
                st.error("Key must be valid hexadecimal.")

with tabs[4]:
    st.subheader("Ed25519 Signing & Verification")
    private_hex = st.text_input("Private key (hex)", type="password")
    public_hex = st.text_input("Public key (hex)", type="password")
    sign_file = st.file_uploader("File to sign / verify", key="sign_file")
    signature = st.file_uploader("Signature file", key="signature_file")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Generate Ed25519 keys", use_container_width=True):
            private, public = generate_ed25519_keys()
            st.code("PRIVATE\n" + private.hex() + "\n\nPUBLIC\n" + public.hex())
    with c2:
        if st.button("Sign file", type="primary", use_container_width=True) and sign_file and private_hex:
            try:
                sig = sign_bytes(bytes.fromhex(private_hex), sign_file.getvalue())
                download_bytes("Download signature", sig, sign_file.name + ".sig")
                audit("sign", sign_file.name)
            except Exception as exc:
                st.error(str(exc))
    if st.button("Verify signature", use_container_width=True) and sign_file and signature and public_hex:
        valid = verify_signature(bytes.fromhex(public_hex), sign_file.getvalue(), signature.getvalue())
        st.success("Signature is valid.") if valid else st.error("Signature verification failed.")
        audit("verify", f"{sign_file.name}: {'valid' if valid else 'invalid'}")

with tabs[5]:
    st.subheader("Key Lab")
    st.write("Generate material for use in the other tabs. The application intentionally does not upload keys anywhere.")
    kind = st.selectbox("Key type", ["AES-256", "HMAC-SHA256", "Ed25519"])
    if st.button("Generate key material", type="primary"):
        if kind == "AES-256":
            key = generate_aes_key()
            st.code(key.hex())
        elif kind == "HMAC-SHA256":
            st.code(generate_hmac_key().hex())
        else:
            private, public = generate_ed25519_keys()
            st.code(f"PRIVATE\n{private.hex()}\n\nPUBLIC\n{public.hex()}")
        audit("key_generation", kind)
    st.warning("Treat private keys and symmetric keys as secrets. This interface displays generated material because it is a key-management laboratory, not a production HSM.")

with tabs[6]:
    st.subheader("Batch Automation")
    st.write("Queue repeatable local operations and export the queue as JSON for later processing or integration with CI/CD.")
    job_type = st.selectbox("Job", ["Hash file", "Analyze sample", "Generate AES key"])
    target = st.text_input("Target / sample", placeholder="path/to/file or sample text")
    if st.button("Add job"):
        job = {"id": secrets.token_hex(6), "type": job_type, "target": target}
        st.session_state.jobs.append(job)
        audit("job_queued", json.dumps(job))
    if st.session_state.jobs:
        st.json(st.session_state.jobs)
        payload = json.dumps(st.session_state.jobs, indent=2).encode()
        download_bytes("Export job queue", payload, "crypto-jobs.json", "application/json")
        if st.button("Clear queue"):
            st.session_state.jobs.clear()
            st.rerun()

with tabs[7]:
    st.subheader("Audit Trail")
    if not st.session_state.audit:
        st.info("No events recorded in this session yet.")
    else:
        st.dataframe(st.session_state.audit, use_container_width=True, hide_index=True)
        report = json.dumps(st.session_state.audit, indent=2).encode()
        download_bytes("Export audit JSON", report, "crypto-audit.json", "application/json")
