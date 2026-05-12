# =======================================================
# Script: core/crypto_hash.py
# Description: Generate Crypto Hash SHA256 from any string
# =======================================================

import random

# SHA256 constants
K_SHA256 = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]

class CryptoHash:
    def __init__(self): # Initialize SHA256 hash
        self.h0 = 0x6a09e667
        self.h1 = 0xbb67ae85
        self.h2 = 0x3c6ef372
        self.h3 = 0xa54ff53a
        self.h4 = 0x510e527f
        self.h5 = 0x9b05688c
        self.h6 = 0x1f83d9ab
        self.h7 = 0x5be0cd19

    def rotate_right(self, n, x) -> int: # Rotate right
        return (n >> x) | (n << (32 - x)) & 0xFFFFFFFF
    
    def ch256_pure(self, mess: bytes) -> bytes: # Compression function
        # Choose input A or input B
        h = [
            0x6a09e667,
            0xbb67ae85,
            0x3c6ef372,
            0xa54ff53a,
            0x510e527f,
            0x9b05688c,
            0x1f83d9ab,
            0x5be0cd19
        ]

        # padding
        mlen = len(mess) * 8
        mess += b'\x80'
        while (len(mess) * 8) % 512 != 448:
            mess += b'\x00'
        mess += mlen.to_bytes(8, byteorder='big') 
        
        # Process message in 512-bit blocks
        for i in range(0, len(mess), 64):
            chunk = mess[i:i+64]
            w = [0] * 64
            # First 16 words are the message block itself
            for j in range(16): 
                w[j] = int.from_bytes(chunk[j*4:j*4+4], byteorder='big')

            # Extend to 64 words
            for j in range(16, 64): 
                s0 = self.rotate_right(w[j-15], 7) ^ self.rotate_right(w[j-15], 18) ^ (w[j-15] >> 3)
                s1 = self.rotate_right(w[j-2], 17) ^ self.rotate_right(w[j-2], 19) ^ (w[j-2] >> 10)
                w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF

            a, b, c, d, e, f, g, hh = h

            # 64 rounds of compression
            for j in range(64):
                S1 = self.rotate_right(e, 6) ^ self.rotate_right(e, 11) ^ self.rotate_right(e, 25)
                ch = (e & f) ^ ((~e) & g)
                temp1 = (hh + S1 + ch + K_SHA256[j] + w[j]) & 0xFFFFFFFF
            
                S0 = self.rotate_right(a, 2) ^ self.rotate_right(a, 13) ^ self.rotate_right(a, 22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (S0 + maj) & 0xFFFFFFFF

                hh, g, f, e = g, f, e, (d + temp1) & 0xFFFFFFFF
            d, c, b, a = c, b, a, (temp1 + temp2) & 0xFFFFFFFF

        # Add the compressed chunk to the initial hash
        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + hh) & 0xFFFFFFFF

        # Concatenate the 8 words to form the 256-bit hash
        return b''.join(val.to_bytes(4, byteorder='big') for val in h)