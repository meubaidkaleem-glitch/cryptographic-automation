from pathlib import Path

from crypto_automation.jobs import Job, run_jobs
from crypto_automation.vault import create_vault, get_key, list_keys, put_key


def test_vault_round_trip(tmp_path: Path):
    vault = tmp_path / "vault.json"
    create_vault(vault, "correct horse battery")
    put_key(vault, "correct horse battery", "demo", "AES-256", b"x" * 32)
    assert list_keys(vault, "correct horse battery")[0]["name"] == "demo"
    kind, value = get_key(vault, "correct horse battery", "demo")
    assert kind == "AES-256"
    assert value == b"x" * 32


def test_batch_hash(tmp_path: Path):
    source = tmp_path / "data.txt"
    source.write_text("hello", encoding="utf-8")
    result = run_jobs([Job("1", "hash", str(source), "sha256")])[0]
    assert result["status"] == "completed"
    assert result["digest"] == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
