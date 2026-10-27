from crypto_automation.crypto import *


def test_aes_roundtrip():
    key = generate_aes_key(); data = b"secret message"
    assert decrypt_bytes(key, encrypt_bytes(key, data)) == data


def test_aes_tamper_rejected():
    key = generate_aes_key(); payload = bytearray(encrypt_bytes(key, b"secret")); payload[-1] ^= 1
    try:
        decrypt_bytes(key, bytes(payload))
        assert False
    except Exception:
        pass


def test_hash(tmp_path):
    p = tmp_path / "a.txt"; p.write_bytes(b"hello")
    assert hash_file(p) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hmac():
    key = generate_hmac_key(); data = b"hello"; tag = create_hmac(key, data)
    assert verify_hmac(key, data, tag)
    assert not verify_hmac(key, b"tampered", tag)


def test_signature():
    private, public = generate_ed25519_keys(); data = b"hello"
    signature = sign_bytes(private, data)
    assert verify_signature(public, data, signature)
    assert not verify_signature(public, b"tampered", signature)
