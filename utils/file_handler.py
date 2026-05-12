"""
file_handler.py — Đọc/Ghi File Chữ Ký và Bao Thư Số
Định dạng: JSON với Base64 encoding
  - .sig.json : Chữ ký số đơn giản
  - .env.json : Bao thư số
"""

import json
import datetime
from pathlib import Path

# --- Constants ---
SIG_EXTENSION = ".sig.json"
ENV_EXTENSION = ".env.json"


def save_signature_file(
    content: str,
    signature_b64: str,
    public_key_pem: str,
    save_path: Path
    ) -> Path:
    """
    Save digital signature file.

    Args:
        content: Original content
        signature_b64: Base64 signature
        public_key_pem: PEM encoded public key
        save_path: File path to save
    
    Returns:
        Path to saved file
    """
    save_path = Path(save_path)
    if not save_path.name.endswith(SIG_EXTENSION):
        save_path = save_path.with_suffix("").with_suffix("") 
        save_path = Path(str(save_path) + SIG_EXTENSION)

    data = {
        "type": "digital_signature",
        "version": "1.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "algorithm": "RSA-PSS-SHA256",
        "content": content,
        "signature": signature_b64,
        "signer_public_key": public_key_pem,
    }

    save_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return save_path

def load_file(path: Path) -> tuple[dict, str]:
    """
    Load digital signature file.

    Args:
        path: File path to load
    
    Returns:
        (data: dict, file_type: "signature" | "envelope")
    
    Raises:
        ValueError: If file is not in valid JSON format
        FileNotFoundError: If file does not exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"File không đúng định dạng JSON: {e}")

    file_type = data.get("type")
    if file_type == "digital_signature":
        return data, "signature"
    elif file_type == "digital_envelope":
        return data, "envelope"
    else:
        raise ValueError(
            f"Loại file không được hỗ trợ: '{file_type}'. "
            "Chỉ hỗ trợ 'digital_signature' và 'digital_envelope'."
        )


def detect_file_type(path: str | Path) -> str | None:
    """
    Detect file type.

    Args:
        path: File path
    
    Returns:
        'signature' | 'envelope' | None
    """
    try:
        _, ftype = load_file(path)
        return ftype
    except Exception:
        return None
