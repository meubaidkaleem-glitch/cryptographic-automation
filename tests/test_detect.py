from crypto_automation.detect import detect_sample


def names(sample: str) -> set[str]:
    return {item.name for item in detect_sample(sample)}


def test_base64_detection():
    assert "Base64" in names("SGVsbG8gd29ybGQ=")


def test_hex_detection():
    assert "Hex / hexadecimal" in names("48656c6c6f")


def test_binary_detection():
    assert "Binary / bit string" in names("01001000 01101001")


def test_url_encoding_detection():
    assert "URL percent-encoding" in names("hello%20world")


def test_jwt_like_detection():
    sample = "eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjMifQ.signature"
    assert "JWT" in names(sample) or "JWT-like token" in names(sample)
