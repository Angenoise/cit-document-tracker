"""
International Data Encryption Algorithm (IDEA) implementation.

This module keeps all encryption work on the backend so the frontend only
receives encrypted document IDs. The code below follows the main IDEA steps:
1. Split the 128-bit key into subkeys.
2. Process the data in 64-bit blocks.
3. Run 8 encryption rounds.
4. Finish with a final output transformation.

The comments in this file are intentionally detailed so the encryption flow
is easy to follow during documentation, maintenance, and demo preparation.
"""

from typing import List, Tuple


class IDEA:
    """IDEA cipher implementation with 52 subkeys and 8 rounds."""

    # IDEA operates on 64-bit blocks, so each block is exactly 8 bytes.
    BLOCK_SIZE = 8  # 64 bits
    # The encryption key must be 128 bits, which is 16 bytes.
    KEY_SIZE = 16   # 128 bits
    # IDEA uses eight main rounds before the final output transformation.
    ROUNDS = 8
    # IDEA needs 52 subkeys in total: 6 per round plus 4 final subkeys.
    TOTAL_SUBKEYS = 52  # 6 per round + 4 for final transformation

    # Modular multiplication uses the special IDEA modulus 65537.
    MOD_PRIME = 65537  # 2^16 + 1

    def __init__(self, key: bytes):
        """
        Initialize the IDEA cipher with a 128-bit key.
        
        Args:
            key: 16 bytes (128 bits) encryption key
        """
        if len(key) != self.KEY_SIZE:
            raise ValueError(f"Key must be {self.KEY_SIZE} bytes, got {len(key)}")

        # Store the key so the same cipher object can encrypt multiple blocks.
        self.key = key
        # Build all 52 subkeys once so the cipher can reuse them for every block.
        self.subkeys = self._generate_subkeys()
    
    @staticmethod
    def _multiplicative_inverse(x: int) -> int:
        """
        Calculate the multiplicative inverse modulo 2^16 + 1.

        IDEA uses this operation during decryption. The special cases for 0 and
        1 are handled explicitly because IDEA defines them differently from the
        normal modular inverse rules.
        """
        # IDEA has special handling for 0 and 1.
        if x == 0:
            return 0
        if x == 1:
            return 1

        # Use the Extended Euclidean Algorithm to find the inverse.
        # t0/t1 track the coefficients while r0/r1 track the remainders.
        t0, t1 = 0, 1
        r0, r1 = IDEA.MOD_PRIME, x

        while r1 != 0:
            quotient = r0 // r1
            t0, t1 = t1, t0 - quotient * t1
            r0, r1 = r1, r0 - quotient * r1

        # Normalize negative results back into the modulus range.
        return t0 if t0 >= 0 else t0 + IDEA.MOD_PRIME
    
    def _generate_subkeys(self) -> List[int]:
        """
        Generate all 52 IDEA subkeys from the 128-bit key.

        IDEA expands the key material so each round gets six 16-bit subkeys.
        The final transformation consumes the last four subkeys.
        
        Returns:
            List of 52 16-bit subkeys
        """
        # Split the 16-byte key into eight 16-bit words.
        # Each pair of bytes becomes one key word.
        key_words = []
        for i in range(8):
            word = (self.key[i * 2] << 8) | self.key[i * 2 + 1]
            key_words.append(word)

        # This list will hold the expanded key material in IDEA order.
        # This list will hold all subkeys in the order IDEA expects them.
        subkeys = []

        # IDEA expands the key by rotating the 128-bit key stream.
        # This loop simulates the key schedule and fills the subkey list.
        for round_num in range(9):  # 8 rounds + 1 final
            for i in range(6 if round_num < 8 else 4):
                # Pick the source word from the original key material.
                idx = (round_num * 6 + i) % 8
                shift = (round_num * 6 + i) // 8

                if idx < len(key_words):
                    word = key_words[idx]
                    if shift % 2 == 0:
                        # Even shifts reuse the word directly.
                        subkeys.append(word)
                    else:
                        # Odd shifts simulate IDEA-style rotation.
                        # The mask keeps the result within 16 bits.
                        rotated = ((word << 25) | (word >> 16)) & 0xFFFF
                        subkeys.append(rotated)

        # Safety check: pad if needed so the list always has 52 values.
        # This should rarely trigger, but it keeps the cipher predictable.
        while len(subkeys) < 52:
            subkeys.append(key_words[len(subkeys) % 8])

        return subkeys[:52]
    
    @staticmethod
    def _modular_add(a: int, b: int) -> int:
        """Add two 16-bit numbers modulo 2^16."""
        # The bit mask keeps the result inside the 0..65535 range.
        return (a + b) & 0xFFFF
    
    @staticmethod
    def _modular_multiply(a: int, b: int) -> int:
        """Multiply two 16-bit numbers modulo (2^16 + 1)."""
        # IDEA treats 0 as 65536 during multiplication.
        if a == 0:
            a = IDEA.MOD_PRIME
        if b == 0:
            b = IDEA.MOD_PRIME

        result = (a * b) % IDEA.MOD_PRIME
        # Convert the special zero result back into the 16-bit representation.
        return result if result != 0 else (IDEA.MOD_PRIME & 0xFFFF)
    
    def _round_function(self, x1: int, x2: int, x3: int, x4: int, 
                       subkey_idx: int) -> Tuple[int, int, int, int]:
        """
        Perform one round of IDEA.

        Each round mixes four 16-bit input words with six round subkeys.
        The output is rearranged and fed into the next round.
        
        Args:
            x1, x2, x3, x4: Four 16-bit input words
            subkey_idx: Starting index in subkeys array
        
        Returns:
            Four 16-bit output words
        """
        # Each round consumes exactly six subkeys.
        k1, k2, k3, k4, k5, k6 = (
            self.subkeys[subkey_idx],
            self.subkeys[subkey_idx + 1],
            self.subkeys[subkey_idx + 2],
            self.subkeys[subkey_idx + 3],
            self.subkeys[subkey_idx + 4],
            self.subkeys[subkey_idx + 5],
        )

        # Step 1: mix the input words with the first four subkeys.
        # Two words use multiplication and two use modular addition.
        y1 = self._modular_multiply(x1, k1)
        y2 = self._modular_add(x2, k2)
        y3 = self._modular_add(x3, k3)
        y4 = self._modular_multiply(x4, k4)

        # Step 2: combine the middle values.
        # These intermediate values drive diffusion across the block.
        u = self._modular_add(y1, y3)
        v = self._modular_add(y2, y4)

        # Step 3: use the last two subkeys to create the round's diffusion.
        u = self._modular_multiply(u, k5)
        v = self._modular_add(v, u)
        v = self._modular_multiply(v, k6)
        u = self._modular_add(u, v)

        # Step 4: XOR the results back into the output words.
        # The output ordering follows the IDEA specification.
        return (
            y1 ^ u,
            y3 ^ v,
            y2 ^ u,
            y4 ^ v
        )
    
    def encrypt_block(self, plaintext: bytes) -> bytes:
        """
        Encrypt a single 64-bit block.
        
        Args:
            plaintext: 8 bytes (64 bits)
        
        Returns:
            8 bytes (64 bits) encrypted data
        """
        if len(plaintext) != 8:
            raise ValueError("Block size must be 8 bytes")

        # Break the 8-byte block into four 16-bit numbers.
        # IDEA processes data as four 16-bit words per round.
        x1 = (plaintext[0] << 8) | plaintext[1]
        x2 = (plaintext[2] << 8) | plaintext[3]
        x3 = (plaintext[4] << 8) | plaintext[5]
        x4 = (plaintext[6] << 8) | plaintext[7]

        # Run the 8 IDEA rounds in order.
        # The tuple order matches the round function's expected input layout.
        for round_num in range(8):
            x1, x3, x2, x4 = self._round_function(x1, x2, x3, x4, round_num * 6)

        # The final transformation uses the last four subkeys.
        k1 = self.subkeys[48]
        k2 = self.subkeys[49]
        k3 = self.subkeys[50]
        k4 = self.subkeys[51]

        # Finish the block with the final mix.
        # This step is the IDEA output transformation before serialization.
        y1 = self._modular_multiply(x1, k1)
        y2 = self._modular_add(x2, k3)
        y3 = self._modular_add(x3, k2)
        y4 = self._modular_multiply(x4, k4)

        # Put the four 16-bit values back into an 8-byte result.
        # The byte order is big-endian to match the input layout.
        ciphertext = bytes([
            (y1 >> 8) & 0xFF, y1 & 0xFF,
            (y2 >> 8) & 0xFF, y2 & 0xFF,
            (y3 >> 8) & 0xFF, y3 & 0xFF,
            (y4 >> 8) & 0xFF, y4 & 0xFF,
        ])
        
        return ciphertext
    
    def decrypt_block(self, ciphertext: bytes) -> bytes:
        """
        Decrypt a single 64-bit block.
        
        Args:
            ciphertext: 8 bytes (64 bits) encrypted data
        
        Returns:
            8 bytes (64 bits) plaintext
        """
        if len(ciphertext) != 8:
            raise ValueError("Block size must be 8 bytes")

        # Break the encrypted block into four 16-bit words.
        # Decryption starts from the ciphertext layout produced by encryption.
        y1 = (ciphertext[0] << 8) | ciphertext[1]
        y2 = (ciphertext[2] << 8) | ciphertext[3]
        y3 = (ciphertext[4] << 8) | ciphertext[5]
        y4 = (ciphertext[6] << 8) | ciphertext[7]

        # Build reversed subkey groups for the decryption process.
        # IDEA decryption uses the inverse order of the encryption schedule.
        inverse_subkeys = []
        for i in range(8):
            idx = 48 - i * 6
            k1_inv = self._multiplicative_inverse(self.subkeys[idx])
            k4_inv = self._multiplicative_inverse(self.subkeys[idx + 3])
            k2 = self.subkeys[idx + 1]
            k3 = self.subkeys[idx + 2]
            k5 = self.subkeys[idx + 4]
            k6 = self.subkeys[idx + 5]

            inverse_subkeys.extend([k1_inv, k3, k2, k4_inv, k5, k6])

        # Undo the final transformation first.
        # This mirrors the last step of encrypt_block in reverse.
        k1_inv = self._multiplicative_inverse(self.subkeys[48])
        k4_inv = self._multiplicative_inverse(self.subkeys[51])
        k2 = self.subkeys[50]
        k3 = self.subkeys[49]

        x1 = self._modular_multiply(y1, k1_inv)
        x2 = self._modular_add(y2, k2)
        x3 = self._modular_add(y3, k3)
        x4 = self._modular_multiply(y4, k4_inv)

        # Work backward through the 8 rounds.
        # Each iteration reverses one encryption round.
        for round_num in range(8):
            idx = (7 - round_num) * 6
            k1_inv = self._multiplicative_inverse(self.subkeys[idx])
            k4_inv = self._multiplicative_inverse(self.subkeys[idx + 3])
            k2 = self.subkeys[idx + 2]
            k3 = self.subkeys[idx + 1]
            k5 = self.subkeys[idx + 4]
            k6 = self.subkeys[idx + 5]

            # Reverse the XOR-mix and modular operations.
            # The round equations are unwound step by step here.
            u = x1 ^ x3
            v = x2 ^ x4

            u = self._modular_multiply(u, k5)
            v = self._modular_add(v, u)
            v = self._modular_multiply(v, k6)
            u = self._modular_add(u, v)

            y1 = self._modular_multiply(x1, k1_inv)
            y2 = self._modular_add(x3, u)
            y3 = self._modular_add(x2, v)
            y4 = self._modular_multiply(x4, k4_inv)

            x1, x2, x3, x4 = y1, y2, y3, y4

        # Convert the recovered words back to an 8-byte plaintext block.
        # This restores the original big-endian byte order.
        plaintext = bytes([
            (x1 >> 8) & 0xFF, x1 & 0xFF,
            (x2 >> 8) & 0xFF, x2 & 0xFF,
            (x3 >> 8) & 0xFF, x3 & 0xFF,
            (x4 >> 8) & 0xFF, x4 & 0xFF,
        ])
        
        return plaintext
    
    def encrypt(self, plaintext: bytes, key: bytes = None) -> bytes:
        """
        Encrypt plaintext using ECB mode (for document IDs).
        
        Args:
            plaintext: Data to encrypt
            key: Optional key (if different from initialization key)
        
        Returns:
            Encrypted data
        """
        if key and key != self.key:
            # Allow a caller to swap in a different key if needed.
            self.key = key
            self.subkeys = self._generate_subkeys()

        # ECB mode needs the input length to be a multiple of 8 bytes.
        # Padding keeps the final block aligned for block encryption.
        padding_len = (8 - (len(plaintext) % 8)) % 8
        plaintext = plaintext + bytes([padding_len] * padding_len)

        # Encrypt each 8-byte chunk separately.
        # This is the simplest block-by-block mode for document IDs.
        ciphertext = b''
        for i in range(0, len(plaintext), 8):
            ciphertext += self.encrypt_block(plaintext[i:i+8])
        
        return ciphertext
    
    def decrypt(self, ciphertext: bytes, key: bytes = None) -> bytes:
        """
        Decrypt ciphertext using ECB mode.
        
        Args:
            ciphertext: Data to decrypt
            key: Optional key (if different from initialization key)
        
        Returns:
            Decrypted data
        """
        if key and key != self.key:
            # Rebuild subkeys if a different key is supplied.
            self.key = key
            self.subkeys = self._generate_subkeys()

        # Decrypt each 8-byte chunk one by one.
        # ECB means each block can be processed independently.
        plaintext = b''
        for i in range(0, len(ciphertext), 8):
            plaintext += self.decrypt_block(ciphertext[i:i+8])

        # Remove the simple zero/length-style padding added during encryption.
        # The last byte stores the padding length in this implementation.
        padding_len = plaintext[-1]
        return plaintext[:-padding_len] if padding_len > 0 else plaintext


def generate_encryption_key(seed: str = None) -> bytes:
    """
    Generate a random 128-bit encryption key.
    
    Args:
        seed: Optional seed for reproducible keys
    
    Returns:
        16 bytes of key material
    """
    import hashlib
    import os
    
    if seed:
        # A seed gives a repeatable key, which is useful for testing.
        # This is helpful when you want stable encryption output in demos.
        hash_obj = hashlib.sha256(seed.encode())
        return hash_obj.digest()[:16]
    else:
        # No seed means we want a fresh random key.
        # os.urandom provides cryptographically secure random bytes.
        return os.urandom(16)


def encrypt_document_id(document_id: str, key: bytes) -> str:
    """
    Encrypt a document ID and return as a hexadecimal string.
    
    Args:
        document_id: Document ID string to encrypt
        key: 16-byte encryption key
    
    Returns:
        Hexadecimal string of encrypted ID
    """
    # Keep only the first 8 bytes because IDEA encrypts one 64-bit block here.
    # The result is padded with null bytes if the ID is shorter than 8 bytes.
    doc_id_bytes = document_id.encode()[:8].ljust(8, b'\x00')
    
    # Create the cipher with the backend-only key.
    # The frontend never sees this key; it only receives the ciphertext.
    cipher = IDEA(key)
    encrypted = cipher.encrypt_block(doc_id_bytes)
    
    # Hex is safe to store in the database and safe to place in QR codes.
    return encrypted.hex().upper()


def decrypt_document_id(encrypted_hex: str, key: bytes) -> str:
    """
    Decrypt an encrypted document ID from a hexadecimal string.
    
    Args:
        encrypted_hex: Hexadecimal string of encrypted ID
        key: 16-byte encryption key
    
    Returns:
        Original document ID string
    """
    encrypted = bytes.fromhex(encrypted_hex)
    # Use the same key to reverse the encryption.
    # Decryption only works when the exact same key material is provided.
    cipher = IDEA(key)
    decrypted = cipher.decrypt_block(encrypted)
    
    # Remove any trailing null bytes from the original padded document ID.
    return decrypted.rstrip(b'\x00').decode('ascii', errors='ignore')
