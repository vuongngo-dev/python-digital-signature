# ======================================================================
# Script: test/test_module_key_manager.py
# Description: Unit tests for key_manager — generate, save, load, list
# Run with: pytest test/test_module_key_manager.py -v
# ======================================================================

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

import pytest
import controller.key_manager as km
from controller.key_manager import (
    generate_key_pair,
    load_private_key,
    load_public_key,
    list_key_pairs,
    get_public_key_pem,
)
from controller.signer import Signer


# ─── Fixture: redirect KEYS_DIR to a temp folder ─────────────────────────────

@pytest.fixture(autouse=True)
def isolated_keys_dir(tmp_path, monkeypatch):
    """
    Redirect KEYS_DIR to a temporary directory for every test so that
    tests are fully isolated and don't pollute the project's keys/ folder.
    """
    monkeypatch.setattr(km, "KEYS_DIR", tmp_path / "keys")


# ─── generate_key_pair ────────────────────────────────────────────────────────

def test_generate_creates_both_files():
    """generate_key_pair must create exactly two PEM files."""
    priv_path, pub_path = generate_key_pair("alice", bits=512)
    assert priv_path.exists(), "Private key file must exist"
    assert pub_path.exists(),  "Public key file must exist"


def test_generate_filename_convention():
    """Generated files must follow the <name>_private.pem / <name>_public.pem convention."""
    priv_path, pub_path = generate_key_pair("bob", bits=512)
    assert priv_path.name == "bob_private.pem"
    assert pub_path.name  == "bob_public.pem"


def test_generate_pem_has_headers():
    """PEM files must contain custom RSA header/footer lines."""
    priv_path, pub_path = generate_key_pair("carol", bits=512)

    priv_text = priv_path.read_text(encoding="utf-8")
    pub_text  = pub_path.read_text(encoding="utf-8")

    assert "-----BEGIN CUSTOM RSA PRIVATE KEY-----" in priv_text
    assert "-----END CUSTOM RSA PRIVATE KEY-----"   in priv_text
    assert "-----BEGIN CUSTOM RSA PUBLIC KEY-----"  in pub_text
    assert "-----END CUSTOM RSA PUBLIC KEY-----"    in pub_text


def test_generate_sanitizes_name():
    """Special characters in the name must be stripped from the filename."""
    priv_path, pub_path = generate_key_pair("my key!@#$", bits=512)
    assert "!" not in priv_path.name
    assert "@" not in priv_path.name
    assert priv_path.exists()
    assert pub_path.exists()


def test_generate_empty_name_falls_back_to_key():
    """An empty (or all-special-char) name must fall back to 'key'."""
    priv_path, pub_path = generate_key_pair("!@#$", bits=512)
    assert priv_path.name == "key_private.pem"
    assert pub_path.name  == "key_public.pem"


# ─── load_private_key ─────────────────────────────────────────────────────────

def test_load_private_key_returns_tuple():
    """load_private_key must return a (d, n) tuple of ints."""
    priv_path, _ = generate_key_pair("dave", bits=512)
    d, n = load_private_key(priv_path)
    assert isinstance(d, int)
    assert isinstance(n, int)
    assert d > 0
    assert n > 0


def test_load_private_key_missing_file():
    """load_private_key must raise FileNotFoundError for a nonexistent path."""
    with pytest.raises(FileNotFoundError):
        load_private_key("/tmp/does_not_exist_private.pem")


def test_load_private_key_corrupt_file(tmp_path, monkeypatch):
    """load_private_key must raise ValueError when the file is corrupt."""
    monkeypatch.setattr(km, "KEYS_DIR", tmp_path / "keys")
    corrupt = tmp_path / "bad_private.pem"
    corrupt.write_text("this is not a valid pem", encoding="utf-8")
    with pytest.raises((ValueError, Exception)):
        load_private_key(corrupt)


# ─── load_public_key ──────────────────────────────────────────────────────────

def test_load_public_key_returns_tuple():
    """load_public_key must return an (e, n) tuple of ints."""
    _, pub_path = generate_key_pair("eve", bits=512)
    e, n = load_public_key(pub_path)
    assert isinstance(e, int)
    assert isinstance(n, int)


def test_load_public_key_exponent_is_65537():
    """Public exponent must always be 65537 (standard Fermat prime)."""
    _, pub_path = generate_key_pair("frank", bits=512)
    e, _ = load_public_key(pub_path)
    assert e == 65537


def test_load_public_key_missing_file():
    """load_public_key must raise FileNotFoundError for a nonexistent path."""
    with pytest.raises(FileNotFoundError):
        load_public_key("/tmp/does_not_exist_public.pem")


# ─── Key consistency ──────────────────────────────────────────────────────────

def test_private_and_public_share_same_modulus():
    """The modulus n must be identical in both the private and public key."""
    priv_path, pub_path = generate_key_pair("grace", bits=512)
    d, n_priv = load_private_key(priv_path)
    e, n_pub  = load_public_key(pub_path)
    assert n_priv == n_pub, "Modulus n must be the same in both keys"


def test_roundtrip_sign_verify_with_loaded_keys():
    """Keys saved and then loaded must still work for sign/verify."""
    priv_path, pub_path = generate_key_pair("heidi", bits=512)
    private_key = load_private_key(priv_path)
    public_key  = load_public_key(pub_path)

    signer   = Signer()
    document = b"Important document content"

    signature = signer.sign(document, private_key)
    assert signer.verify(document, signature, public_key) is True


def test_tampered_document_fails_verification():
    """Verification must fail if the document is altered after signing."""
    priv_path, pub_path = generate_key_pair("ivan", bits=512)
    private_key = load_private_key(priv_path)
    public_key  = load_public_key(pub_path)

    signer    = Signer()
    original  = b"Original content"
    tampered  = b"Tampered content"

    signature = signer.sign(original, private_key)
    assert signer.verify(tampered, signature, public_key) is False


# ─── list_key_pairs ───────────────────────────────────────────────────────────

def test_list_key_pairs_empty_initially():
    """list_key_pairs must return an empty list when no keys exist."""
    assert list_key_pairs() == []


def test_list_key_pairs_after_generation():
    """list_key_pairs must detect all generated key pairs."""
    generate_key_pair("judy",  bits=512)
    generate_key_pair("kevin", bits=512)

    pairs = list_key_pairs()
    names = {p["name"] for p in pairs}

    assert "judy"  in names
    assert "kevin" in names


def test_list_key_pairs_has_correct_flags():
    """Each entry must have correct has_private / has_public flags."""
    generate_key_pair("leo", bits=512)

    pairs = list_key_pairs()
    leo = next(p for p in pairs if p["name"] == "leo")

    assert leo["has_private"] is True
    assert leo["has_public"]  is True
    assert leo["private_path"].exists()
    assert leo["public_path"].exists()


# ─── get_public_key_pem ───────────────────────────────────────────────────────

def test_get_public_key_pem_returns_string():
    """get_public_key_pem must return the PEM content as a string."""
    _, pub_path = generate_key_pair("mia", bits=512)
    pem = get_public_key_pem(pub_path)
    assert isinstance(pem, str)
    assert "PUBLIC" in pem


# ─── Run directly ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
