# Hash assword with Argon2
# Verify a submitted passworf against its stored hash.
# Create signed JWT access tokens.
# Decode and validate JWTs including their expiration.

from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.config import settings

Password_Hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Return a secure hash of a plain-text password"""
    return Password_Hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Check a password against its stored hash"""
    return Password_Hash.verify(plain_password, hashed_password)


def create_access_token(
        subject: str,
        role: str,
) -> str:
    """Create a signed JWT with an expiration date"""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """verify the jwt signeture and expiration, then return its claims."""
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "exp"]},
    )

    return payload