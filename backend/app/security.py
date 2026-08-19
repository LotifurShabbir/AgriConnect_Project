"""
Password hashing utilities.

Uses PBKDF2-HMAC-SHA256 from the standard library so registration
endpoints never store plaintext passwords, without pulling in an
extra third-party dependency for this basic flow.
"""

import hashlib
import hmac
import os

_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Hash a plaintext password with a random per-user salt."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Check a plaintext password against a hash produced by hash_password()."""
    salt_hex, digest_hex = stored_hash.split("$")
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return hmac.compare_digest(actual, expected)
