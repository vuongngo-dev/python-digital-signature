## ======================================================================
# Script: test/test_rsa.py
# Description: Generate RSA Keypair and test RSA signing and verification
# ======================================================================

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.crypto_rsa import CryptoRSA

def test_rsa():
    crypto_rsa = CryptoRSA()
    private_key, public_key = crypto_rsa.generate_rsa_keypair()
    
    print("private_key: ", private_key)
    print("public_key: ", public_key)
    
if __name__ == "__main__":
    test_rsa()
