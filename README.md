# AutoCrypt

**AutoCrypt** is a local-first professional cryptographic automation workbench combining a multi-tab Streamlit application, terminal tooling, automatic encoding/sample analysis, an encrypted development key vault, batch execution, and structured audit reporting.

## What AutoCrypt does

AutoCrypt is designed as a complete workflow rather than a collection of isolated crypto commands:

```text
INPUT
  |
  +--> SAMPLE / TEXT
  |       |
  |       +--> Encoding Analyzer
  |              +--> Base64 / Base64URL
  |              +--> Base32
  |              +--> Hex / Binary
  |              +--> URL encoding
  |              +--> JWT-like structures
  |              +--> UTF-8 / plain text
  |              +--> entropy diagnostics
  |
  +--> ARTIFACT
  |       |
  |       +--> Hash / HMAC
  |       +--> AES-256-GCM encryption/decryption
  |       +--> Ed25519 signing/verification
  |
  +--> KEY MATERIAL
          |
          +--> encrypted local development vault
          +--> AES-256 / HMAC / Ed25519 key generation

                 |
                 v
          Batch Automation
                 |
                 v
          Audit & Reporting
```

## Application tabs

1. **Dashboard** — operational metrics and recommended workflow.
2. **Encoding Analyzer** — ranked heuristic detection of common encodings and token structures.
3. **Encrypt / Decrypt** — AES-256-GCM authenticated artifact protection.
4. **Hash & HMAC** — SHA-256, SHA-512 and HMAC-SHA256.
5. **Sign & Verify** — Ed25519 digital signatures.
6. **Key Management** — password-protected local encrypted development vault.
7. **Batch Automation** — queue, export and execute repeatable local jobs.
8. **Audit & Reports** — timestamped session events with JSON, CSV and Markdown export.
9. **Settings** — operational limits and production-hardening guidance.

## Encoding detection

AutoCrypt automatically tests samples against common structural representations. It reports confidence, the reason for a match, and a decoded preview where appropriate.

Supported detection includes:

- Base64
- Base64URL
- Base32
- hexadecimal
- binary/bit strings
- URL percent encoding
- JWT and JWT-like structures
- UTF-8/plain text
- high-entropy diagnostic signals

AutoCrypt intentionally does **not** claim that arbitrary ciphertext can be identified as AES, RSA, ChaCha20, etc. from its bytes alone. Reliable algorithm identification normally requires metadata, protocol context, file-format information or known test vectors.

## Cryptographic design

- **AES-256-GCM** for authenticated symmetric encryption.
- **Ed25519** for digital signatures.
- **SHA-256 / SHA-512** for cryptographic digests.
- **HMAC-SHA256** for keyed integrity/authentication.
- OS-backed secure randomness for generated key and nonce material.
- No custom cryptographic primitives.
- Authentication is checked before decrypted plaintext is returned.

## Key management

The local development vault uses a password-derived encryption key and authenticated encryption:

```text
vault password
      |
      v
PBKDF2-HMAC-SHA256
      |
      v
32-byte key
      |
      v
AES-GCM encrypted vault
```

The vault is deliberately documented as a development/control-workflow feature. Production deployments should use an appropriate KMS, HSM or enterprise secret-management service.

## Run AutoCrypt

### Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
streamlit run app.py
```

The CLI is also exposed as:

```bash
autocrypt --help
```

The legacy `crypto-auto` command remains available as a compatibility alias.

### Windows

```powershell
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
streamlit run app.py
```

### Docker

```bash
docker build -t autocrypt .
docker run --rm -p 8501:8501 autocrypt
```

For remote exposure, put AutoCrypt behind appropriate authentication, TLS and network controls. Do not expose a development Streamlit instance directly to an untrusted network.

## Automation model

Batch jobs are represented as structured objects and can currently perform local operations such as file hashing, sample detection and file inspection. The job layer is modular so additional adapters can be added for directory processing, encryption, signing, scheduled workflows and CI/CD pipelines.

## Audit and reporting

The application records session events such as:

- encryption/decryption attempts
- hash generation
- signing and verification
- key-vault operations
- detection operations
- batch execution

Reports can be exported as JSON, CSV or Markdown.

## Repository layout

```text
autocrypt/
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

## Production roadmap

The foundation is intentionally modular for future enterprise capabilities:

- persistent database-backed audit storage
- role-based access control and SSO
- KMS/HSM integrations
- key rotation and lifecycle policies
- multi-file/directory pipelines
- resumable background jobs
- configurable workflow DAGs
- certificate/PKI lifecycle tooling
- signed artifact manifests and provenance
- policy-as-code and algorithm allowlists
- Prometheus/OpenTelemetry observability
- hardened reverse-proxy deployment

## Security note

AutoCrypt is intended for legitimate cryptographic automation, education, development and authorized data-protection workflows. It is not a replacement for professional cryptographic review, an HSM/KMS, or an enterprise secrets-management architecture.

## License

MIT
