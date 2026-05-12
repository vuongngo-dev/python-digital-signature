# ======================================================================
# Script: test/test_hash.py
# Description: Generate Crypto Hash SHA256 from any string
# ======================================================================

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.crypto_hash import CryptoHash

def test_hash():
    crypto_hash = CryptoHash()
    hash_value = crypto_hash.ch256_pure("Hello World".encode())
    hash_2 = crypto_hash.ch256_pure("Hello  World".encode())
    print(hash_value == hash_2)
    return hash_value

if __name__ == "__main__":
    hash_value = test_hash()
    print(hash_value.hex())
