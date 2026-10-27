# AutoCrypt

## Download and install on Windows, macOS, and Linux

AutoCrypt is currently distributed as source code; this repository does not yet publish native EXE, DMG, or Linux installer packages.

### 1. Download the source

- **ZIP (all operating systems):** [Download the latest source ZIP](https://github.com/meubaidkaleem-glitch/cryptographic-automation/archive/refs/heads/main.zip), then extract it.
- **Git:** install Git from https://git-scm.com/downloads, then run:

```bash
git clone https://github.com/meubaidkaleem-glitch/cryptographic-automation.git
cd cryptographic-automation
```

Install Python 3.11 or newer from https://www.python.org/downloads/ if it is not already installed.

### 2. Windows 10/11

Open PowerShell in the extracted project folder:

```powershell
py -3 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
streamlit run app.py
```

If PowerShell activation is blocked, use Command Prompt instead and activate with `.venv\\Scripts\\activate.bat`. When installing Python on Windows, enable the option to add Python to PATH if offered.

### 3. macOS

Open Terminal in the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
streamlit run app.py
```

If a dependency requires Apple's command-line developer tools, install them with `xcode-select --install` and retry.

### 4. Linux (Ubuntu/Debian example)

Install Python and virtual-environment support, then set up AutoCrypt:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
streamlit run app.py
```

Use Python 3.11 or newer. Other Linux distributions may use a different package manager and package names.

### 5. Docker (Windows, macOS, or Linux)

Install Docker Desktop (Windows/macOS) or Docker Engine (Linux), then run these commands from the project folder:

```bash
docker build -t autocrypt .
docker run --rm -p 8501:8501 autocrypt
```

Open http://localhost:8501 in your browser.

### 6. Open AutoCrypt

After the final command, open the local URL printed in the terminal (usually http://localhost:8501). Keep the terminal open while using the app; press Ctrl+C there to stop it. See the [official Streamlit installation guide](https://docs.streamlit.io/get-started/installation/command-line) for more environment details.

---


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
