# =======================================================
# Script: controller/signer.py
# Description: Sign a document with RSA private key
# =======================================================

from typing import Tuple
from core.crypto_hash import CryptoHash

class Signer:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.crypto_hash = CryptoHash()

    def sign(self, content: bytes, private_key: tuple[int, int] = None) -> bytes:
        """
        Signature function for a document.

        Args:
            content (bytes): The document to sign
            private_key (tuple[int, int]): The private key to sign with

        Returns:
            bytes: The signature of the document
        """

        # Use private key from parameter or from class
        key_to_use = private_key or self.private_key
        if not key_to_use:
            raise ValueError("Chưa có Khóa bí mật (Private Key) để ký!")
        
        # TODO: Implement PSS padding
        d, n = key_to_use
        
        # TODO: Hash the content
        hash_bytes = self.crypto_hash.ch256_pure(content)

        # Convert bytes to integer
        hash_int = int.from_bytes(hash_bytes, byteorder='big')

        # Apply RSA signature algorithm
        signature_int = pow(hash_int, d, n)

        # Convert integer to bytes
        byte_length = (n.bit_length() + 7) // 8
        signature_bytes = signature_int.to_bytes(byte_length, byteorder='big')

        return signature_bytes

    def verify(self, content: bytes, signature_bytes: bytes, public_key: tuple[int, int] = None) -> bool:
        """
        verify signature
        """

        # TODO: Implement PSS padding
        key_to_use = public_key or self.public_key
        if not key_to_use:
            raise ValueError("Chưa có Khóa công khai (Public Key) để xác thực!")
        
        # TODO: Convert bytes to integer
        e, n = key_to_use

        # TODO: Convert signature bytes to integer
        original_hash_int = pow(int.from_bytes(signature_bytes, byteorder='big'), e, n)

        # TODO: Hash the content
        hash_bytes = self.crypto_hash.ch256_pure(content)

        # Convert hash bytes to integer for comparison
        hash_int = int.from_bytes(hash_bytes, byteorder='big')
        return original_hash_int == hash_int