# ======================================================================
# Script: test/test_module_sign.py
# Description: Unit tests for RSA signing/verification and SHA-256 hash
# Run with: pytest test/test_module_sign.py -v
# ======================================================================

import hashlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from controller.signer import Signer
from core.crypto_rsa import CryptoRSA
from core.crypto_hash import CryptoHash


# ─── SHA-256 Tests ────────────────────────────────────────────────────────────
def test_sha256_matches_stdlib():
    """Custom SHA-256 must produce the same digest as Python's hashlib."""
    messages = [
        b"Hello World",
        b"",
        b"abc",
        b"The quick brown fox jumps over the lazy dog",
    ]
    crypto_hash = CryptoHash()
    for msg in messages:
        expected = hashlib.sha256(msg).digest()
        actual = crypto_hash.ch256_pure(msg)
        assert actual == expected, (
            f"SHA-256 mismatch for {msg!r}\n"
            f"  expected: {expected.hex()}\n"
            f"  actual  : {actual.hex()}"
        )


# ─── RSA Key Generation Tests ─────────────────────────────────────────────────

def test_rsa_keypair_structure():
    """RSA key pair must have correct structure: (d, n) private, (e, n) public."""
    private_key, public_key = CryptoRSA().generate_rsa_keypair()
    d, n_priv = private_key
    e, n_pub = public_key

    assert n_priv == n_pub, "Modulus n must be the same in both keys"
    assert e == 65537, f"Public exponent must be 65537, got {e}"
    assert d != e, "Private exponent d must differ from e"
    assert n_priv.bit_length() >= 512, "Modulus must be at least 512 bits"


# ─── Sign & Verify Tests ──────────────────────────────────────────────────────

def test_sign_and_verify_valid():
    """Signing then verifying the same document must return True."""
    signer = Signer()
    private_key, public_key = CryptoRSA().generate_rsa_keypair()

    document = b"Hello World"
    signature = signer.sign(document, private_key)

    assert isinstance(signature, bytes), "Signature must be bytes"
    assert len(signature) > 0, "Signature must not be empty"

    is_valid = signer.verify(document, signature, public_key)
    assert is_valid is True, "Verification must return True for a valid signature"


def test_verify_tampered_document():
    """Verification must fail if the document is altered after signing."""
    signer = Signer()
    private_key, public_key = CryptoRSA().generate_rsa_keypair()

    original = b"Original document"
    tampered = b"Tampered document"

    signature = signer.sign(original, private_key)
    is_valid = signer.verify(tampered, signature, public_key)
    assert is_valid is False, "Verification must return False for a tampered document"


def test_verify_wrong_key():
    """Verification must fail if a different public key is used."""
    signer = Signer()
    private_key1, _ = CryptoRSA().generate_rsa_keypair()
    _, public_key2 = CryptoRSA().generate_rsa_keypair()

    document = b"Hello World"
    signature = signer.sign(document, private_key1)

    is_valid = signer.verify(document, signature, public_key2)
    assert is_valid is False, "Verification must fail with a mismatched public key"


def test_sign_raises_without_key():
    """sign() must raise ValueError when no private key is provided."""
    signer = Signer()
    try:
        signer.sign(b"data")
        assert False, "Expected ValueError was not raised"
    except ValueError:
        pass


def test_verify_raises_without_key():
    """verify() must raise ValueError when no public key is provided."""
    signer = Signer()
    try:
        signer.verify(b"data", b"\x00" * 64)
        assert False, "Expected ValueError was not raised"
    except ValueError:
        pass


# ─── Run directly ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])