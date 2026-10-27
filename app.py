from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from pathlib import Path

import streamlit as st

from crypto_automation.crypto import (
    decrypt_bytes,
    encrypt_bytes,
    generate_aes_key,
    generate_ed25519_keys,
    generate_hmac_key,
    sign_bytes,
    verify_signature,
)
from crypto_automation.detect import detect_sample
from crypto_automation.jobs import Job, run_jobs
from crypto_automation.report import event, markdown_report, to_csv, to_json
from crypto_automation.vault import create_vault, delete_key, get_key, list_keys, put_key

st.set_page_config(page_title="Cryptographic Automation", page_icon="CA", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
.block-container {max-width: 1500px; padding-top: 1.5rem;}
.hero {padding: 1.4rem 1.6rem; border: 1px solid rgba(80,160,255,.35); border-radius: 18px; background: linear-gradient(120deg, rgba(0,90,160,.22), rgba(20,25,50,.55)); margin-bottom: 1rem;}
.hero h1 {margin-bottom: .2rem;}
.badge {display:inline-block; padding:.25rem .55rem; border-radius:999px; background:rgba(50,150,255,.16); margin-right:.3rem; font-size:.82rem;}
.small {opacity:.75; font-size:.9rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def init_state() -> None:
    st.session_state.setdefault("jobs", [])
    st.session_state.setdefault("audit", [])
    st.session_state.setdefault("last_detection", [])
    st.session_state.setdefault("settings", {"max_upload_mb": 100, "audit_retention": 1000})


def audit(action: str, detail: str, status: str = "success") -> None:
    st.session_state.audit.insert(0, event(action, detail, status))
    st.session_state.audit = st.session_state.audit[: st.session_state.settings["audit_retention"]]


def download(label: str, data: bytes, filename: str, mime: str = "application/octet-stream") -> None:
    st.download_button(label, data=data, file_name=filename, mime=mime, use_container_width=True)


def parse_key(value: str, expected: int | None = None) -> bytes:
    try:
        raw = bytes.fromhex(value.strip())
    except ValueError as exc:
        raise ValueError("Key must be hexadecimal.") from exc
    if expected is not None and len(raw) != expected:
        raise ValueError(f"Expected exactly {expected} bytes ({expected * 2} hex characters).")
    return raw


def hash_bytes(data: bytes, algorithm: str) -> str:
    return hashlib.new(algorithm.replace("-", "").lower(), data).hexdigest()


init_state()

st.markdown("""
<div class="hero">
<h1>Cryptographic Automation</h1>
<p>Secure • Detect • Encrypt • Verify • Automate • Report</p>
<span class="badge">AES-256-GCM</span><span class="badge">Ed25519</span><span class="badge">SHA-256 / SHA-512</span><span class="badge">HMAC-SHA256</span><span class="badge">Local-first</span>
<p class="small">A professional cryptographic workbench for repeatable defensive workflows. Cryptographic primitives come from the established Python cryptography library; the application does not invent its own algorithms.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Control Center")
    st.markdown("**Workflow**")
    st.markdown("1. Analyze a sample or artifact\n2. Select a protection operation\n3. Generate or retrieve key material\n4. Execute and verify\n5. Queue repeatable jobs\n6. Export evidence and audit records")
    st.divider()
    st.caption("Security boundary")
    st.info("Encoding detection is heuristic. It can identify common representations, but ciphertext alone generally cannot prove which encryption algorithm produced it.")


tabs = st.tabs([
    "Dashboard", "Encoding Analyzer", "Encrypt / Decrypt", "Hash & HMAC",
    "Sign & Verify", "Key Management", "Batch Automation", "Audit & Reports", "Settings"
])

with tabs[0]:
    st.subheader("Operations dashboard")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Queued jobs", len(st.session_state.jobs))
    c2.metric("Audit events", len(st.session_state.audit))
    c3.metric("Detection results", len(st.session_state.last_detection))
    c4.metric("Encryption", "AES-256-GCM")
    c5.metric("Signatures", "Ed25519")
    st.markdown("### Platform scope")
    scope = [
        ("Analyze", "Encoding/format recognition with confidence and decoded previews."),
        ("Protect", "Authenticated encryption, hashing and HMAC integrity workflows."),
        ("Authenticate", "Ed25519 signing and verification of artifacts."),
        ("Manage", "Password-protected local vault for development key material."),
        ("Automate", "JSON-defined repeatable jobs and batch execution."),
        ("Evidence", "Timestamped audit events and JSON/CSV/Markdown reports."),
    ]
    cols = st.columns(3)
    for i, (name, description) in enumerate(scope):
        with cols[i % 3].container(border=True):
            st.markdown(f"**{name}**")
            st.write(description)
    st.markdown("### Recommended operational flow")
    st.code("Input → Analyze → Transform → Protect → Verify → Automate → Report", language="text")

with tabs[1]:
    st.subheader("Encoding & Sample Analyzer")
    st.caption("Paste text or a token. The engine tests multiple common encodings and returns ranked evidence rather than pretending to identify unknown encryption.")
    sample = st.text_area("Sample", height=190, placeholder="Example: SGVsbG8gd29ybGQ=", key="sample")
    if st.button("Analyze sample", type="primary", use_container_width=True):
        if not sample.strip():
            st.warning("Provide a sample first.")
        else:
            results = detect_sample(sample)
            st.session_state.last_detection = results
            audit("sample_analysis", f"Analyzed {len(sample)} characters; {len(results)} interpretations returned.")
    if st.session_state.last_detection:
        for result in st.session_state.last_detection[:10]:
            with st.container(border=True):
                a, b, c = st.columns([1.1, 1.2, 4])
                a.metric("Confidence", f"{result.confidence:.0%}")
                b.markdown(f"**{result.name}**\n\n`{result.category}`")
                c.write(result.reason)
                if result.decoded_preview:
                    c.code(result.decoded_preview, language="text")
        st.warning("A successful encoding match is not proof that the original source was benign, secure, or cryptographically protected. Treat unknown samples as untrusted data.")

with tabs[2]:
    st.subheader("AES-256-GCM Protection")
    operation = st.radio("Operation", ["Encrypt", "Decrypt"], horizontal=True)
    uploaded = st.file_uploader("Input artifact", key="enc_file")
    key_text = st.text_input("AES-256 key (hex)", type="password", help="64 hexadecimal characters = 32 bytes.", key="aes_key")
    if operation == "Encrypt":
        if st.button("Encrypt artifact", type="primary", use_container_width=True):
            if not uploaded:
                st.warning("Choose a file first.")
            else:
                try:
                    key = parse_key(key_text, 32) if key_text else generate_aes_key()
                    result = encrypt_bytes(key, uploaded.getvalue())
                    download("Download .enc container", result, uploaded.name + ".enc")
                    if not key_text:
                        st.warning("A new key was generated. Store it securely; it is required for decryption.")
                        st.code(key.hex())
                    st.success("AES-256-GCM encryption and authentication completed.")
                    audit("encrypt", uploaded.name)
                except Exception as exc:
                    audit("encrypt", str(exc), "failed")
                    st.error(str(exc))
    else:
        if st.button("Decrypt and authenticate", type="primary", use_container_width=True):
            if not uploaded or not key_text:
                st.warning("Choose the encrypted file and provide its key.")
            else:
                try:
                    plaintext = decrypt_bytes(parse_key(key_text, 32), uploaded.getvalue())
                    name = uploaded.name[:-4] if uploaded.name.endswith(".enc") else uploaded.name + ".recovered"
                    download("Download recovered artifact", plaintext, name)
                    st.success("Authentication passed and plaintext was recovered.")
                    audit("decrypt", uploaded.name)
                except Exception:
                    audit("decrypt", f"{uploaded.name}: authentication/decryption failed", "failed")
                    st.error("Decryption failed. The key, container or authentication tag may be invalid.")

with tabs[3]:
    st.subheader("Hashing & HMAC")
    file_for_hash = st.file_uploader("Artifact", key="hash_artifact")
    alg = st.selectbox("Digest algorithm", ["SHA-256", "SHA-512"])
    if file_for_hash:
        digest = hash_bytes(file_for_hash.getvalue(), alg)
        st.markdown(f"**{alg}**")
        st.code(digest)
        if st.button("Add hash event", use_container_width=True):
            audit("hash", f"{alg} generated for {file_for_hash.name}")
    st.divider()
    st.markdown("### HMAC-SHA256")
    hmac_file = st.file_uploader("HMAC artifact", key="hmac_artifact")
    hmac_key_text = st.text_input("HMAC key (hex)", type="password", key="hmac_key")
    h1, h2 = st.columns(2)
    with h1:
        if st.button("Generate HMAC key"):
            generated = generate_hmac_key()
            st.session_state["generated_hmac"] = generated.hex()
    with h2:
        if "generated_hmac" in st.session_state:
            st.code(st.session_state["generated_hmac"])
    if hmac_file and hmac_key_text:
        try:
            tag = hmac.new(parse_key(hmac_key_text), hmac_file.getvalue(), hashlib.sha256).hexdigest()
            st.markdown("**Authentication tag**")
            st.code(tag)
            st.caption("Store the key separately from the tag. The tag alone cannot authenticate future data.")
        except ValueError as exc:
            st.error(str(exc))

with tabs[4]:
    st.subheader("Ed25519 Digital Signatures")
    sign_mode = st.radio("Mode", ["Sign", "Verify"], horizontal=True)
    artifact = st.file_uploader("Artifact", key="signature_artifact")
    if sign_mode == "Sign":
        private = st.text_input("Private key (hex)", type="password", key="sign_private")
        if st.button("Sign artifact", type="primary", use_container_width=True):
            if not artifact or not private:
                st.warning("Provide an artifact and private key.")
            else:
                try:
                    sig = sign_bytes(parse_key(private, 32), artifact.getvalue())
                    download("Download signature", sig, artifact.name + ".sig")
                    st.success("Ed25519 signature created.")
                    audit("sign", artifact.name)
                except Exception as exc:
                    st.error(str(exc))
    else:
        public = st.text_input("Public key (hex)", type="password", key="verify_public")
        sig = st.file_uploader("Signature", key="verify_sig")
        if st.button("Verify signature", type="primary", use_container_width=True):
            if not artifact or not public or not sig:
                st.warning("Provide the artifact, public key and signature.")
            else:
                try:
                    valid = verify_signature(parse_key(public, 32), artifact.getvalue(), sig.getvalue())
                    if valid:
                        st.success("VALID — signature matches the supplied artifact.")
                        audit("verify_signature", artifact.name)
                    else:
                        st.error("INVALID — signature verification failed.")
                        audit("verify_signature", artifact.name, "failed")
                except ValueError as exc:
                    st.error(str(exc))

with tabs[5]:
    st.subheader("Key Management")
    st.caption("This is a local development vault, not a replacement for an HSM/KMS in production. The vault contents are encrypted with a password-derived key and authenticated encryption.")
    vault_path = st.text_input("Vault file", value=".cryptoauto/vault.json")
    vault_password = st.text_input("Vault password", type="password")
    v1, v2, v3 = st.columns(3)
    with v1:
        if st.button("Create vault", use_container_width=True):
            try:
                create_vault(vault_path, vault_password)
                audit("vault_create", vault_path)
                st.success("Vault created.")
            except Exception as exc:
                st.error(str(exc))
    with v2:
        if st.button("List vault keys", use_container_width=True):
            try:
                st.json(list_keys(vault_path, vault_password))
            except Exception:
                st.error("Vault could not be opened. Check the path and password.")
    with v3:
        if st.button("Delete selected key", use_container_width=True):
            name = st.session_state.get("vault_selected")
            if not name:
                st.warning("Select a key name below first.")
            else:
                try:
                    delete_key(vault_path, vault_password, name)
                    audit("vault_delete", name)
                    st.success("Key removed from vault.")
                except Exception as exc:
                    st.error(str(exc))
    st.divider()
    key_name = st.text_input("Key name", value="my-aes-key")
    key_kind = st.selectbox("Generate", ["AES-256", "HMAC-SHA256", "Ed25519 private key"])
    if st.button("Generate and store", type="primary"):
        try:
            if key_kind == "AES-256":
                value = generate_aes_key(); kind = "AES-256"
            elif key_kind == "HMAC-SHA256":
                value = generate_hmac_key(); kind = "HMAC-SHA256"
            else:
                value, _ = generate_ed25519_keys(); kind = "Ed25519-private"
            put_key(vault_path, vault_password, key_name, kind, value)
            audit("vault_store", f"{key_name} ({kind})")
            st.success(f"Stored {key_name} in the encrypted vault.")
        except Exception as exc:
            st.error(str(exc))
    selected = st.text_input("Key to retrieve", key="vault_selected_input")
    if selected:
        st.session_state.vault_selected = selected
        if st.button("Retrieve key material"):
            try:
                kind, value = get_key(vault_path, vault_password, selected)
                st.code(f"TYPE: {kind}\nVALUE: {value.hex()}")
                audit("vault_retrieve", selected)
            except Exception:
                st.error("Key could not be retrieved.")

with tabs[6]:
    st.subheader("Batch Automation")
    st.caption("Queue jobs, export them, and execute supported local operations as a batch.")
    job_action = st.selectbox("Action", ["hash", "detect", "inspect-file"])
    job_input = st.text_input("Input path", placeholder="/path/to/file.txt")
    job_algorithm = st.selectbox("Algorithm", ["sha256", "sha512"])
    job_output = st.text_input("Optional output path")
    if st.button("Queue job", type="primary"):
        if not job_input:
            st.warning("Input path is required.")
        else:
            job = Job(secrets.token_hex(6), job_action, job_input, job_algorithm, job_output)
            st.session_state.jobs.append(job)
            audit("job_queued", f"{job.action}: {job.input}")
    if st.session_state.jobs:
        st.json([job.__dict__ for job in st.session_state.jobs])
        j1, j2 = st.columns(2)
        with j1:
            if st.button("Execute queued jobs", use_container_width=True):
                results = run_jobs(st.session_state.jobs)
                st.session_state["last_job_results"] = results
                audit("batch_execute", f"Executed {len(results)} jobs")
        with j2:
            payload = json.dumps({"jobs": [job.__dict__ for job in st.session_state.jobs]}, indent=2).encode()
            download("Export job definition", payload, "crypto-jobs.json", "application/json")
        if st.button("Clear queue"):
            st.session_state.jobs.clear(); st.rerun()
    if st.session_state.get("last_job_results"):
        st.markdown("### Results")
        st.json(st.session_state.last_job_results)

with tabs[7]:
    st.subheader("Audit & Reports")
    if not st.session_state.audit:
        st.info("No events have been recorded in this session.")
    else:
        st.dataframe(st.session_state.audit, use_container_width=True, hide_index=True)
        json_data = to_json(st.session_state.audit)
        csv_data = to_csv(st.session_state.audit)
        md_data = markdown_report(st.session_state.audit)
        r1, r2, r3 = st.columns(3)
        with r1: download("JSON report", json_data, "crypto-audit.json", "application/json")
        with r2: download("CSV report", csv_data, "crypto-audit.csv", "text/csv")
        with r3: download("Markdown report", md_data, "crypto-audit.md", "text/markdown")

with tabs[8]:
    st.subheader("Settings & Operational Policy")
    st.session_state.settings["max_upload_mb"] = st.number_input("Maximum upload size (MB)", min_value=1, max_value=2048, value=int(st.session_state.settings["max_upload_mb"]))
    st.session_state.settings["audit_retention"] = st.number_input("Maximum audit events retained", min_value=10, max_value=10000, value=int(st.session_state.settings["audit_retention"]))
    st.markdown("### Production hardening checklist")
    st.checkbox("Use an external KMS/HSM for production secrets", value=False, disabled=True)
    st.checkbox("Restrict the application behind authenticated access", value=False, disabled=True)
    st.checkbox("Enable centralized immutable audit storage", value=False, disabled=True)
    st.checkbox("Use TLS when the UI is remotely exposed", value=False, disabled=True)
    st.caption("These controls are deployment requirements rather than switches that can make a local Streamlit process production-secure by themselves.")
