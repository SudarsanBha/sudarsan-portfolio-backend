# Hash assword with Argon2
# Verify a submitted passworf against its stored hash.
# Create signed JWT access tokens.
# Decode and validate JWTs including their expiration.

from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

from app.config import settings
# Refresh token
from uuid import uuid4
import hashlib


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


def hash_refresh_token(token: str) -> str:
    """Return a SHA-256 hash of a refresh token."""
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_access_token(
        subject: str,
        role: str,
) -> str:
    """Create a signed JWT access token with an expiration date"""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def create_refresh_token(
        subject: str,
        role: str,
) -> str:
    """Create a longer-lived JWT refresh token."""

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": subject,
        "role": role,
        "type": "refresh",
        "jti": str(uuid4()),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.refresh_token_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """verify the jwt signeture and expiration, then return its claims."""

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "exp", "type"]},
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid access token type")

    if not payload["sub"]:
        raise jwt.InvalidTokenError("Access token subject cannot be empty.")

    return payload

def decode_refresh_token(token: str) -> dict:
    """Validate a refresh token and return its class."""

    payload = jwt.decode(
        token,
        settings.refresh_token_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": ["sub", "exp", "jti", "type",],
        },
    )

    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Invalid Refresh Token type.")

    if not payload["jti"]:
        raise jwt.InvalidTokenError("Refresh token ID cannot be empty.")

    if not payload["sub"]:
        raise jwt.InvalidTokenError("Refresh tokensubject cannot be empty.")

    return payload