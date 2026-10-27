# Cryptographic Automation

A local-first cryptographic automation platform combining a professional Streamlit workbench, terminal tooling, an encoding/sample detection engine, an encrypted development key vault, batch execution, and structured audit reporting.

## What is implemented

### Application workbench

Run the UI with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
streamlit run app.py
```

The application provides:

1. **Dashboard** — operational metrics, supported primitives and workflow overview.
2. **Encoding Analyzer** — ranked detection of Base64, Base64URL, Base32, hex, binary, URL encoding, JWT-like structures, UTF-8/plain text and high-entropy indicators.
3. **Encrypt / Decrypt** — AES-256-GCM authenticated encryption for uploaded artifacts.
4. **Hash & HMAC** — SHA-256, SHA-512 and HMAC-SHA256 workflows.
5. **Sign & Verify** — Ed25519 artifact signing and signature verification.
6. **Key Management** — password-protected local encrypted vault for development key material.
7. **Batch Automation** — queue, export and execute repeatable local jobs.
8. **Audit & Reports** — session events with JSON, CSV and Markdown export.
9. **Settings** — operational limits and production-hardening guidance.

## Complete workflow

```text
                 +---------------------+
                 |       INPUT         |
                 | text / file / key   |
                 +----------+----------+
                            |
          +-----------------+------------------+
          |                                    |
          v                                    v
 +------------------+                 +-------------------+
 | Sample Analyzer  |                 | Artifact Pipeline |
 | Base64/Base32    |                 | hash / HMAC       |
 | hex/binary/URL   |                 | encrypt/decrypt   |
 | JWT-like/UTF-8   |                 | sign/verify       |
 +---------+--------+                 +---------+---------+
           |                                    |
           +----------------+-------------------+
                            v
                 +---------------------+
                 |   Key Management    |
                 | local encrypted     |
                 | development vault   |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 | Batch Automation    |
                 | queue -> execute    |
                 | -> capture results  |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 | Audit & Reporting   |
                 | JSON / CSV / MD     |
                 +---------------------+
```

## Detection model

The analyzer is deliberately conservative about cryptographic identification.

It can recognize structural representations such as Base64 or hexadecimal because those formats have observable syntax. It can also report high entropy as a diagnostic signal. It **does not claim that an arbitrary ciphertext can be identified as AES, RSA, ChaCha20 or another algorithm solely from its bytes**. Correct algorithm identification normally requires metadata, protocol context, file format information or known test vectors.

## Cryptographic design

- **AES-256-GCM** for authenticated symmetric encryption.
- **Ed25519** for digital signatures.
- **SHA-256 / SHA-512** for cryptographic digests.
- **HMAC-SHA256** for keyed integrity/authentication.
- OS-backed randomness through Python's secure random facilities for key/nonce generation.
- No custom cryptographic primitives.
- Authentication is checked before decrypted plaintext is returned.

## Key vault

The local development vault uses:

```text
password
   |
   v
PBKDF2-HMAC-SHA256
   |
   v
32-byte encryption key
   |
   v
AES-GCM encrypted vault
```

The vault is intended for local development and controlled workflows. Production deployments should use an appropriate KMS/HSM or secret-management service rather than treating a Streamlit process as a hardware-backed key boundary.

## Batch automation

Jobs are represented as structured objects and can currently perform:

- file hashing
- sample detection from a text file
- file inspection

The job engine is intentionally modular so additional adapters can be added for encryption, signing, directory traversal, scheduled workflows and CI/CD pipelines.

## Audit and reporting

The workbench records session events such as:

- encryption/decryption attempts
- hash generation
- signing and verification
- key-vault operations
- detection operations
- batch execution

Reports can be exported as JSON, CSV or Markdown.

## Deployment

### Local

```bash
streamlit run app.py
```

### Docker

```bash
docker build -t cryptographic-automation .
docker run --rm -p 8501:8501 cryptographic-automation
```

For remote exposure, place the application behind appropriate authentication, TLS and network controls. Do not expose a development Streamlit instance directly to an untrusted network.

## CI

GitHub Actions runs the Python test suite on pushes and pull requests. The test suite covers the core crypto workflows, encoding detection, vault round trips and batch hashing.

## Repository layout

```text
cryptographic-automation/
├── app.py
├── crypto_automation/
│   ├── cli.py
│   ├── crypto.py
│   ├── detect.py
│   ├── jobs.py
│   ├── report.py
│   └── vault.py
├── tests/
│   ├── test_crypto.py
│   ├── test_detect.py
│   └── test_vault_and_jobs.py
├── .github/workflows/test.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Roadmap for production scale

The current repository is a substantial working foundation. The next engineering layer for a production deployment would be:

- persistent database-backed audit storage
- role-based access control and SSO
- external KMS/HSM integrations
- key rotation and lifecycle policies
- multi-file/directory pipelines with resumable jobs
- configurable workflow DAGs
- background workers and progress tracking
- stronger artifact manifests and provenance
- certificate/PKI lifecycle tooling
- signed release manifests
- policy-as-code and algorithm allowlists
- Prometheus/OpenTelemetry observability
- deployment manifests and hardened reverse-proxy configuration

## Security note

This project is intended for legitimate defensive cryptographic automation, education, development and authorized data-protection workflows. Never use generated keys or test workflows as a substitute for a properly reviewed production key-management architecture.

## License

MIT
