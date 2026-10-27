# Cryptographic Automation

A local-first cryptographic automation workbench that combines a Python CLI with a multi-tab Streamlit application.

The goal is to make routine cryptographic work repeatable, inspectable and safer: analyze a sample, identify likely encodings, transform data, encrypt or authenticate it, sign and verify artifacts, generate key material, queue automation jobs, and review an audit trail.

## Application

Launch the graphical workbench:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
streamlit run app.py
```

Or, after installation:

```bash
crypto-auto-app
```

## Complete workflow

```text
INPUT
  |
  +--> Text/sample ----------> Encoding Analyzer
  |                              |
  |                              +--> Base64 / Base64URL
  |                              +--> Base32
  |                              +--> Hex
  |                              +--> Binary
  |                              +--> URL percent-encoding
  |                              +--> JWT-like structure
  |                              +--> UTF-8/plain text
  |                              +--> Entropy diagnostic
  |
  +--> File -----------------> Hash & HMAC
  |                              |
  |                              +--> SHA-256 / SHA-512
  |                              +--> HMAC-SHA256
  |
  +--> File -----------------> Encrypt / Decrypt
  |                              |
  |                              +--> AES-256-GCM
  |
  +--> File -----------------> Sign & Verify
  |                              |
  |                              +--> Ed25519
  |
  +--> Key material ----------> Key Lab
                                 |
                                 +--> AES-256
                                 +--> HMAC-SHA256
                                 +--> Ed25519

                         |
                         v
                    Batch Jobs
                         |
                         v
                    Audit Trail
```

## Tabs

### 1. Dashboard

A high-level workspace showing current session jobs, audit events and the supported cryptographic capabilities.

### 2. Encoding Analyzer

Paste a sample and receive ranked heuristic detections. The analyzer currently checks:

- Base64
- Base64URL
- Base32
- hexadecimal
- binary/bit strings
- URL percent-encoding
- JWT and JWT-like structures
- UTF-8/plain text
- high-entropy diagnostic signals

The application deliberately distinguishes **encoding detection** from **encryption identification**. A Base64 wrapper can be detected from its structure; an unknown ciphertext cannot reliably reveal its encryption algorithm simply from a sample.

### 3. Encrypt / Decrypt

AES-256-GCM provides authenticated encryption. The implementation generates a fresh nonce for every encryption operation and verifies authentication before releasing decrypted plaintext.

### 4. Hash & HMAC

Calculate SHA-256/SHA-512 digests and generate HMAC-SHA256 authentication tags for files.

### 5. Sign & Verify

Generate Ed25519 keys, sign files and verify signatures. This is useful for release artifacts, configuration files and integrity-sensitive documents.

### 6. Key Lab

Generate symmetric and signing key material for development and controlled local workflows. The interface warns that displayed private material should be treated as secret and that this tab is not an HSM.

### 7. Batch Jobs

Queue repeatable jobs and export the queue as JSON for automation or CI/CD integration. The architecture is intentionally designed so more job adapters can be added without changing the cryptographic primitives.

### 8. Audit

Review actions performed during the current application session and export the audit events as JSON.

## CLI capabilities

The original CLI remains available alongside the application for terminal automation and scripting. The project uses established primitives from the `cryptography` package rather than implementing cryptographic algorithms from scratch.

## Security model

- AES-GCM is used instead of unauthenticated raw encryption.
- AES-256 keys are exactly 32 bytes.
- Fresh random nonces are generated for AES-GCM operations.
- Ed25519 is used for digital signatures.
- Key generation uses the operating system's secure random source.
- Unknown or unsupported algorithms are rejected rather than silently substituted.
- Encoding detection is explicitly heuristic and does not claim to identify unknown encryption schemes.
- Secret material is not sent to a remote service by the Streamlit application.

## Project layout

```text
cryptographic-automation/
├── app.py                         # Streamlit multi-tab application
├── crypto_automation/
│   ├── __init__.py
│   ├── cli.py                     # terminal interface
│   ├── crypto.py                  # cryptographic primitives/workflows
│   └── detect.py                  # sample/encoding detection engine
├── tests/
│   └── test_crypto.py
├── pyproject.toml
└── README.md
```

## Development

```bash
pip install -e '.[dev]'
pytest -q
```

## Roadmap

The next expansion points are intentionally separated from the core cryptography:

- persistent encrypted key storage and rotation workflows
- directory and multi-file batch processing
- richer encoding/format recognition
- configurable automation pipelines
- structured JSON/CSV/PDF reporting
- background job execution with progress and cancellation
- plugin adapters for additional cryptographic formats
- CI/CD workflow templates
- stronger audit persistence and tamper-evident audit records

## License

MIT
