# ======================================================================
# Script: test/test_module_file_handler.py
# Description: Unit tests for utils/file_handler.py
# Run with: pytest test/test_module_file_handler.py -v
# ======================================================================

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

import pytest
from utils.file_handler import (
    save_signature_file,
    load_file,
    detect_file_type,
    SIG_EXTENSION,
    ENV_EXTENSION,
)


def test_save_signature_file(tmp_path):
    """save_signature_file must create a valid JSON file with correct extension and contents."""
    content = "This is a test document"
    signature_b64 = "base64_encoded_signature_string"
    public_key_pem = "-----BEGIN PUBLIC KEY-----\nkey\n-----END PUBLIC KEY-----"
    
    # Provide a path without extension
    save_path = tmp_path / "test_doc"
    
    result_path = save_signature_file(content, signature_b64, public_key_pem, save_path)
    
    assert result_path.name == f"test_doc{SIG_EXTENSION}"
    assert result_path.exists()
    
    # Verify contents
    saved_data = json.loads(result_path.read_text(encoding="utf-8"))
    assert saved_data["type"] == "digital_signature"
    assert saved_data["version"] == "1.0"
    assert "timestamp" in saved_data
    assert saved_data["algorithm"] == "RSA-PSS-SHA256"
    assert saved_data["content"] == content
    assert saved_data["signature"] == signature_b64
    assert saved_data["signer_public_key"] == public_key_pem


def test_save_signature_file_with_existing_extension(tmp_path):
    """If the path already has .sig.json, it shouldn't append it again."""
    content = "Test"
    save_path = tmp_path / f"already_has_ext{SIG_EXTENSION}"
    
    result_path = save_signature_file(content, "sig", "pub", save_path)
    assert result_path.name == f"already_has_ext{SIG_EXTENSION}"


def test_load_file_signature(tmp_path):
    """load_file should correctly parse a digital_signature file."""
    test_file = tmp_path / "valid_sig.json"
    data = {"type": "digital_signature", "content": "hello"}
    test_file.write_text(json.dumps(data), encoding="utf-8")
    
    loaded_data, file_type = load_file(test_file)
    assert loaded_data == data
    assert file_type == "signature"


def test_load_file_envelope(tmp_path):
    """load_file should correctly parse a digital_envelope file."""
    test_file = tmp_path / "valid_env.json"
    data = {"type": "digital_envelope", "encrypted_key": "..."}
    test_file.write_text(json.dumps(data), encoding="utf-8")
    
    loaded_data, file_type = load_file(test_file)
    assert loaded_data == data
    assert file_type == "envelope"


def test_load_file_not_found():
    """load_file should raise FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        load_file(Path("/path/that/does/not/exist.json"))


def test_load_file_invalid_json(tmp_path):
    """load_file should raise ValueError for malformed JSON."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("this is not json", encoding="utf-8")
    
    with pytest.raises(ValueError, match="File không đúng định dạng JSON"):
        load_file(bad_file)


def test_load_file_unsupported_type(tmp_path):
    """load_file should raise ValueError for unknown 'type' field."""
    unsupported = tmp_path / "unsupported.json"
    data = {"type": "unknown_type"}
    unsupported.write_text(json.dumps(data), encoding="utf-8")
    
    with pytest.raises(ValueError, match="Loại file không được hỗ trợ"):
        load_file(unsupported)


def test_detect_file_type(tmp_path):
    """detect_file_type should return the correct type string or None on failure."""
    sig_file = tmp_path / "sig.json"
    sig_file.write_text(json.dumps({"type": "digital_signature"}), encoding="utf-8")
    
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({"type": "digital_envelope"}), encoding="utf-8")
    
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("invalid json", encoding="utf-8")
    
    assert detect_file_type(sig_file) == "signature"
    assert detect_file_type(env_file) == "envelope"
    assert detect_file_type(bad_file) is None
    assert detect_file_type(Path("/nonexistent")) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
