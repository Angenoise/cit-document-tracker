#!/usr/bin/env python
"""
Utility script to test IDEA encryption algorithm
Run: python test_encryption.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from encryption.idea import IDEA, encrypt_document_id, decrypt_document_id, generate_encryption_key


def test_basic_encryption():
    """Test basic IDEA encryption and decryption"""
    print("\n" + "="*60)
    print("TEST 1: Basic IDEA Encryption/Decryption")
    print("="*60)
    
    # Generate a key
    key = generate_encryption_key("test-seed")
    print(f"✓ Generated key: {key.hex().upper()}")
    
    # Create cipher
    cipher = IDEA(key)
    print(f"✓ Created IDEA cipher with {len(cipher.subkeys)} subkeys")
    
    # Test plaintext block (exactly 8 bytes)
    plaintext = b"TEST1234"
    print(f"✓ Plaintext:  {plaintext.hex().upper()}")
    
    # Encrypt
    ciphertext = cipher.encrypt_block(plaintext)
    print(f"✓ Encrypted:  {ciphertext.hex().upper()}")
    
    # Decrypt
    decrypted = cipher.decrypt_block(ciphertext)
    print(f"✓ Decrypted:  {decrypted.hex().upper()}")
    
    # Verify
    if plaintext == decrypted:
        print("✓ ✅ ENCRYPTION TEST PASSED")
        return True
    else:
        print("✗ ❌ ENCRYPTION TEST FAILED")
        return False


def test_document_id_encryption():
    """Test document ID encryption/decryption"""
    print("\n" + "="*60)
    print("TEST 2: Document ID Encryption")
    print("="*60)
    
    # Generate key
    key = generate_encryption_key("doc-encryption-key")
    doc_id = "550e8400"  # First 8 chars of a UUID
    
    print(f"✓ Document ID: {doc_id}")
    print(f"✓ Encryption key: {key.hex().upper()}")
    
    # Encrypt
    encrypted_hex = encrypt_document_id(doc_id, key)
    print(f"✓ Encrypted:   {encrypted_hex}")
    
    # Verify it's 32 hex characters (16 bytes)
    if len(encrypted_hex) == 32:
        print(f"✓ Encrypted ID is correct length: {len(encrypted_hex)} chars")
    else:
        print(f"✗ Invalid encrypted ID length: {len(encrypted_hex)}")
        return False
    
    # Decrypt
    decrypted = decrypt_document_id(encrypted_hex, key)
    print(f"✓ Decrypted:   {decrypted.rstrip(chr(0))}")
    
    # Verify
    if doc_id in decrypted:
        print("✓ ✅ DOCUMENT ID ENCRYPTION TEST PASSED")
        return True
    else:
        print("✗ ❌ DOCUMENT ID ENCRYPTION TEST FAILED")
        return False


def test_multiple_encryptions():
    """Test that same plaintext produces same ciphertext (ECB deterministic)"""
    print("\n" + "="*60)
    print("TEST 3: ECB Mode Determinism")
    print("="*60)
    
    key = generate_encryption_key("determinism-test")
    cipher = IDEA(key)
    
    plaintext = b"ECBTEST!"
    
    # Encrypt twice
    ciphertext1 = cipher.encrypt_block(plaintext)
    ciphertext2 = cipher.encrypt_block(plaintext)
    
    print(f"✓ Plaintext:    {plaintext.hex().upper()}")
    print(f"✓ Ciphertext 1: {ciphertext1.hex().upper()}")
    print(f"✓ Ciphertext 2: {ciphertext2.hex().upper()}")
    
    if ciphertext1 == ciphertext2:
        print("✓ ✅ DETERMINISM TEST PASSED (ECB mode)"
              "\n   (Note: ECB is deterministic - same plaintext → same ciphertext)")
        return True
    else:
        print("✗ ❌ DETERMINISM TEST FAILED")
        return False


def test_different_keys():
    """Test that different keys produce different ciphertexts"""
    print("\n" + "="*60)
    print("TEST 4: Different Keys Produce Different Results")
    print("="*60)
    
    key1 = generate_encryption_key("key-one")
    key2 = generate_encryption_key("key-two")
    
    cipher1 = IDEA(key1)
    cipher2 = IDEA(key2)
    
    plaintext = b"KEYTEST!"
    
    ciphertext1 = cipher1.encrypt_block(plaintext)
    ciphertext2 = cipher2.encrypt_block(plaintext)
    
    print(f"✓ Plaintext:    {plaintext.hex().upper()}")
    print(f"✓ Key 1:        {key1.hex().upper()}")
    print(f"✓ Ciphertext 1: {ciphertext1.hex().upper()}")
    print(f"✓ Key 2:        {key2.hex().upper()}")
    print(f"✓ Ciphertext 2: {ciphertext2.hex().upper()}")
    
    if ciphertext1 != ciphertext2:
        print("✓ ✅ DIFFERENT KEYS TEST PASSED")
        return True
    else:
        print("✗ ❌ DIFFERENT KEYS TEST FAILED")
        return False


def test_subkey_generation():
    """Test that 52 subkeys are generated correctly"""
    print("\n" + "="*60)
    print("TEST 5: Subkey Generation")
    print("="*60)
    
    key = generate_encryption_key("subkey-test")
    cipher = IDEA(key)
    
    print(f"✓ Generated {len(cipher.subkeys)} subkeys (expected: 52)")
    
    if len(cipher.subkeys) == 52:
        print("✓ ✅ SUBKEY GENERATION TEST PASSED")
        
        # Show some statistics
        print(f"\n  Subkey Statistics:")
        print(f"  - Min value: {min(cipher.subkeys):5d} (0x{min(cipher.subkeys):04X})")
        print(f"  - Max value: {max(cipher.subkeys):5d} (0x{max(cipher.subkeys):04X})")
        print(f"  - Avg value: {sum(cipher.subkeys)//len(cipher.subkeys)}")
        
        return True
    else:
        print("✗ ❌ SUBKEY GENERATION TEST FAILED")
        return False


def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█  CIT DOCUMENT TRACKER - IDEA ENCRYPTION TEST SUITE".ljust(59) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        ("Basic Encryption", test_basic_encryption),
        ("Document ID Encryption", test_document_id_encryption),
        ("ECB Determinism", test_multiple_encryptions),
        ("Different Keys", test_different_keys),
        ("Subkey Generation", test_subkey_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ❌ {test_name} FAILED WITH EXCEPTION:")
            print(f"   {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("-"*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED! IDEA encryption is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
