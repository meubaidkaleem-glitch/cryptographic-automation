# Cryptographic Automation

A practical, security-focused Python toolkit for automating common cryptographic workflows from a single CLI.

## What it does

- Generate cryptographically secure AES-256 keys.
- Encrypt and decrypt files with AES-256-GCM (authenticated encryption).
- Hash files with SHA-256/SHA-512.
- Generate and verify HMACs for integrity/authenticity checks.
- Generate Ed25519 signing keys and sign/verify files.
- Run repeatable batch jobs from a YAML configuration file.
- Produce JSON-friendly output for CI/CD and automation pipelines.
- Refuse unsafe defaults such as unauthenticated encryption or weak algorithms.

> This project is for defensive, legitimate cryptographic automation. It does not implement custom cryptographic primitives; it uses well-reviewed primitives from the `cryptography` library.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

crypto-auto keygen aes --output secret.key
crypto-auto encrypt secret.key document.txt document.enc
crypto-auto decrypt secret.key document.enc document.txt.recovered
crypto-auto hash document.txt --algorithm sha256
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

## Signing

```bash
crypto-auto keygen ed25519 --private-key signing.key --public-key signing.pub
crypto-auto sign signing.key document.txt document.sig
crypto-auto verify signing.pub document.txt document.sig
```

## Batch automation

Create `crypto.yml`:

```yaml
jobs:
  - name: release-hash
    action: hash
    input: dist/release.zip
    algorithm: sha256
    output: dist/release.sha256
```

Run it with:

```bash
crypto-auto batch crypto.yml
```

## Security design

- AES-GCM provides confidentiality and integrity; every encryption operation uses a fresh random nonce.
- Keys are generated with the operating system's cryptographically secure random source.
- Ed25519 is used for signatures instead of rolling a signature scheme from scratch.
- File writes are atomic where practical and sensitive key files are created with restrictive permissions on POSIX systems.
- The CLI never prints secret key material unless explicitly requested by a future command designed for that purpose.
- Algorithms are explicit and reject unknown values instead of silently falling back.

## Project layout

```text
cryptographic-automation/
├── crypto_automation/
│   ├── cli.py          # command-line interface
│   ├── crypto.py       # cryptographic operations
│   └── batch.py        # YAML automation runner
├── tests/
│   └── test_crypto.py
├── examples/
│   └── crypto.yml
├── pyproject.toml
└── README.md
```

## Development

```bash
pip install -e '.[dev]'
pytest -q
```

## License

MIT
