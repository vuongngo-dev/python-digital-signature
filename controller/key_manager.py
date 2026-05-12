# =======================================================
# Script: controller/key_manager.py
# Description: Key pair management
# =======================================================

import json
import base64
from pathlib import Path
from core.crypto_rsa import CryptoRSA

KEYS_DIR = Path(__file__).parent.parent / "keys"

# ─── Internal PEM-like serialization ─────────────────────────────────────────

def _encode_pem(data: dict, key_type: str) -> str:
    """Serialize a key dict to a PEM-like text block (Base64-wrapped JSON)."""
    json_bytes = json.dumps(data).encode("utf-8")
    b64 = base64.b64encode(json_bytes).decode("ascii")
    lines = [b64[i:i+64] for i in range(0, len(b64), 64)]
    header = f"-----BEGIN CUSTOM RSA {key_type} KEY-----"
    footer = f"-----END CUSTOM RSA {key_type} KEY-----"
    return header + "\n" + "\n".join(lines) + "\n" + footer + "\n"


def _decode_pem(pem_content: str) -> dict:
    """Deserialize a PEM-like text block back to a key dict."""
    lines = [l for l in pem_content.strip().splitlines() if not l.startswith("-----")]
    b64 = "".join(lines)
    json_bytes = base64.b64decode(b64)
    return json.loads(json_bytes)


# ─── Directory helpers ────────────────────────────────────────────────────────

def ensure_keys_dir():
    """Ensure keys directory exists."""
    KEYS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_key_pair(name: str, bits: int = 512) -> tuple[Path, Path]:
    """
    Generate and save an RSA key pair.

    Args:
        name: Logical name for the key pair (used as filename prefix).
        bits: RSA key size in bits (default 512 for speed; use 2048+ in production).

    Returns:
        (private_key_path, public_key_path)
    """
    ensure_keys_dir()

    crypto_rsa = CryptoRSA(bits=bits)
    public_key, private_key = crypto_rsa.generate_rsa_keypair()  # (e,n), (d,n)

    e, n = public_key
    d, _  = private_key

    private_pem = _encode_pem({"d": d, "n": n, "key_type": "private"}, "PRIVATE")
    public_pem  = _encode_pem({"e": e, "n": n, "key_type": "public"},  "PUBLIC")

    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
    if not safe_name:
        safe_name = "key"

    private_path = KEYS_DIR / f"{safe_name}_private.pem"
    public_path  = KEYS_DIR / f"{safe_name}_public.pem"

    private_path.write_text(private_pem, encoding="utf-8")
    public_path.write_text(public_pem,   encoding="utf-8")

    return private_path, public_path


def load_private_key(path: str | Path) -> tuple[int, int]:
    """
    Load private key from PEM file.

    Args:
        path: Path to the private key PEM file.

    Returns:
        (d, n) — private key tuple.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed as a private key.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    try:
        data = _decode_pem(path.read_text(encoding="utf-8"))
        return (data["d"], data["n"])
    except (KeyError, Exception) as e:
        raise ValueError(f"Không thể load private key: {e}")


def load_public_key(path: str | Path) -> tuple[int, int]:
    """
    Load public key from PEM file.

    Args:
        path: Path to the public key PEM file.

    Returns:
        (e, n) — public key tuple.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed as a public key.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    try:
        data = _decode_pem(path.read_text(encoding="utf-8"))
        return (data["e"], data["n"])
    except (KeyError, Exception) as e:
        raise ValueError(f"Không thể load public key: {e}")


def list_key_pairs() -> list[dict]:
    """
    List all key pairs in the keys/ directory.

    Returns:
        List of dicts: [{name, private_path, public_path, has_private, has_public}]
    """
    ensure_keys_dir()
    key_map: dict[str, dict] = {}

    for f in sorted(KEYS_DIR.glob("*.pem")):
        stem = f.stem
        if stem.endswith("_private"):
            base = stem[:-8]
            key_map.setdefault(base, {})["private"] = f
            key_map[base]["name"] = base
        elif stem.endswith("_public"):
            base = stem[:-7]
            key_map.setdefault(base, {})["public"] = f
            key_map[base]["name"] = base

    return [
        {
            "name":         info.get("name", base),
            "private_path": info.get("private"),
            "public_path":  info.get("public"),
            "has_private":  "private" in info,
            "has_public":   "public"  in info,
        }
        for base, info in key_map.items()
    ]


def get_public_key_pem(path: str | Path) -> str:
    """
    Read the PEM content of a public key file as a string.

    Args:
        path: Path to the public key PEM file.

    Returns:
        PEM content as a string.
    """
    return Path(path).read_text(encoding="utf-8")
