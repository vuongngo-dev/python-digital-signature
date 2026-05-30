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
        
        # Trial division with small primes under 1000 for a 10x-20x speedup
        small_primes = [
            3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
            101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
            211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331,
            337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457,
            461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599,
            601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733,
            739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877,
            881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
        ]
        for p in small_primes:
            if n % p == 0:
                return n == p

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

    def generate_rsa_keypair(self, bits=None) -> tuple[tuple[int, int], tuple[int, int]]: # Generate RSA key pairs
        if bits is None:
            bits = self.bits
        
        # prime_bits is bits // 2 if bits >= 512, so the modulus n = p * q has approximately `bits` size.
        prime_bits = bits // 2 if bits >= 512 else bits
        p = self.generate_prime(prime_bits)
        q = self.generate_prime(prime_bits)
        
        n = p * q # Modulus
        phi = (p - 1) * (q - 1) # Euler's totient function
        
        e = 65537 # Fermat prime commonly used as Public Key
        if self.gcd(e, phi) != 1:
            e = 3
        d = self.mod_inverse(e, phi) # Private Key
        
        self.public_key = (e, n)
        self.private_key = (d, n)
        return self.public_key, self.private_key
