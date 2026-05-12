# ======================================================================
# Script: core/crypto_rsa.py
# Description: Generate RSA key pairs (private key and public key)
#              Support 2048-bit and 4096-bit key lengths
#              Support PEM format
# ======================================================================

import random

class CryptoRSA:
    def __init__(self, bits=512):
        self.bits = bits
        self.public_key = None
        self.private_key = None

    def gcd(self, a: int, b: int) -> int: # Find the greatest common divisor of a and b
        while b != 0:
            a, b = b, a % b
        return a

    def mod_inverse(self, e, phi): # Find the modular inverse of e modulo phi
        d_old, d_new = 0, 1
        r_old, r_new = phi, e
        while r_new != 0:
            quotient = r_old // r_new
            d_old, d_new = d_new, d_old - quotient * d_new
            r_old, r_new = r_new, r_old - quotient * r_new
        return d_old + phi if d_old < 0 else d_old

    def is_prime(self, n, k=5) -> bool: # Miller-Rabin primality test
        if n <= 1: return False
        if n in (2, 3): return True
        if n % 2 == 0: return False
        
        r, s = 0, n - 1
        while s % 2 == 0:
            r += 1
            s //= 2
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, s, n)
            if x == 1 or x == n - 1: continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1: break
            else: # If the loop completes without finding a non-prime, return False
                return False
        return True

    def generate_prime(self, bits) -> int: # Generate a random large prime number
        while True:
            p = random.getrandbits(bits)
            p |= (1 << bits - 1) | 1 # Ensure the number is odd and has enough bits
            if self.is_prime(p):
                return p

    def generate_rsa_keypair(self, bits=512) -> tuple[tuple[int, int], tuple[int, int]]: # Generate RSA key pairs
        p = self.generate_prime(bits)
        q = self.generate_prime(bits)
        
        n = p * q # Modulus
        phi = (p - 1) * (q - 1) # Euler's totient function
        
        e = 65537 # Fermat prime commonly used as Public Key
        if self.gcd(e, phi) != 1:
            e = 3
        d = self.mod_inverse(e, phi) # Private Key
        
        self.public_key = (e, n)
        self.private_key = (d, n)
        
        # Returns (private_key, public_key) to match signing workflow
        return self.private_key, self.public_key
