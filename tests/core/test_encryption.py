"""Tests for neuraprop_core.encryption — AES-256-GCM field-level encryption."""

import pytest

from neuraprop_core.encryption import encrypt_value, decrypt_value


class TestEncryption:
    def test_roundtrip(self):
        """Encrypt then decrypt returns original plaintext."""
        plaintext = "sensitive trader data"
        encrypted = encrypt_value(plaintext)
        decrypted = decrypt_value(encrypted)
        assert decrypted == plaintext

    def test_different_ciphertexts(self):
        """Same plaintext produces different ciphertexts (random nonce)."""
        plaintext = "same input"
        e1 = encrypt_value(plaintext)
        e2 = encrypt_value(plaintext)
        assert e1 != e2
        # But both decrypt to the same value
        assert decrypt_value(e1) == plaintext
        assert decrypt_value(e2) == plaintext

    def test_empty_string(self):
        """Can encrypt and decrypt empty strings."""
        encrypted = encrypt_value("")
        assert decrypt_value(encrypted) == ""

    def test_unicode(self):
        """Handles unicode characters correctly."""
        plaintext = "Trad\u00e9r N\u00e4me \u2603"
        encrypted = encrypt_value(plaintext)
        assert decrypt_value(encrypted) == plaintext

    def test_long_value(self):
        """Handles long values."""
        plaintext = "x" * 10000
        encrypted = encrypt_value(plaintext)
        assert decrypt_value(encrypted) == plaintext

    def test_tampered_ciphertext_fails(self):
        """Tampered ciphertext raises an error."""
        encrypted = encrypt_value("secret")
        # Flip a character in the middle
        tampered = encrypted[:10] + ("A" if encrypted[10] != "A" else "B") + encrypted[11:]
        with pytest.raises(Exception):
            decrypt_value(tampered)

    def test_encrypted_is_base64(self):
        """Encrypted output is valid base64."""
        import base64
        encrypted = encrypt_value("test")
        # Should not raise
        base64.b64decode(encrypted)
