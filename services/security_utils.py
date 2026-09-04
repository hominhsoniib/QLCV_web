"""
Security utilities: password hashing & verification.

Uses the `bcrypt` library directly (not passlib) because the installed
passlib version has a known incompatibility with modern bcrypt releases
(passlib tries to read bcrypt.__about__.__version__, which no longer
exists in bcrypt>=4.1, causing a runtime crash on every hash/verify call).

All new and updated passwords in this system MUST go through
`hash_password()` before being stored. Nothing should ever compare a
raw incoming password directly against a stored value again.
"""
import bcrypt

_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")


def hash_password(plain_password: str) -> str:
    """Hashes a plaintext password with bcrypt. Returns a UTF-8 string safe to store in a String column."""
    plain_password = str(plain_password or "")
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def is_bcrypt_hash(value: str) -> bool:
    """Returns True if the stored value already looks like a bcrypt hash."""
    value = str(value or "")
    return value.startswith(_BCRYPT_PREFIXES) and len(value) >= 59


def verify_password(plain_password: str, stored_value: str) -> bool:
    """Verifies a plaintext password against whatever is stored.

    - If the stored value is a bcrypt hash, verifies properly with bcrypt.
    - If the stored value is legacy plaintext (pre-migration accounts),
      falls back to a direct comparison so existing accounts keep working.
      Callers should re-hash and save the password immediately after a
      successful legacy-plaintext match (see `auth_service.check_login`).

    NOTE: No hardcoded backdoor / universal passwords are permitted here.
    Every comparison is against the specific user's own stored credential.
    """
    plain_password = str(plain_password or "")
    stored_value = str(stored_value or "")
    if not plain_password or not stored_value:
        return False

    if is_bcrypt_hash(stored_value):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_value.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    # Legacy plaintext account (not yet migrated). Exact match only —
    # no case-insensitive fallback, no shared/default password list.
    return plain_password == stored_value
