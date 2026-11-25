from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import update
from sqlalchemy.orm import Session
from app.models.refresh_tokens import RefreshToken
from app.security import (
    create_refresh_token,
    decode_refresh_token,
    hash_refresh_token
)
from app.models.users import User

class RefreshTokenReuseError(Exception):
    """Raise when an alredy-revoked refresh token is reused."""

    def __init__(self, family_id: str):
        self.family_id = family_id
        super().__init__("Refresh token reuse detected")


def create_and_store_refresh_token(
        db: Session,
        user_id: int,
        family_id: str | None = None,
) -> str:
    """Generate a refresh token and store its hashed record"""

    # Verify that the user exists and is active.
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise ValueError(
            "Cannot create a refresh token for an inactive or missing user."
        )

    # Generate the JWT refresh token.
    token = create_refresh_token(
        subject=str(user_id),
        role=user.role,
    )

    # Decode it to retrive its claims.
    payload = decode_refresh_token(token)

    # Convert the JWT expiration timesdtamp into a datetime.
    expires_at = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc,
    )

    # Create a database record
    refresh_token_record = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(token),
        jti=payload["jti"],
        family_id=family_id or str(uuid4()),
        expires_at=expires_at,
    )

    # Add the record to the database Session.
    db.add(refresh_token_record)
    db.flush()

    return token


def get_refresh_token_record(
    db: Session,
    token: str,
) -> RefreshToken | None:
    """Find a refresh-token record using its SHA-256 hash."""

    token_hash = hash_refresh_token(token)

    return (
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    )


def revoke_refresh_token(
        db: Session,
        token_record: RefreshToken,
) -> None:
    """Revoke an individual refresh token."""

    if token_record.revoked_at is not None:
        return 
    
    token_record.revoked_at = datetime.now(timezone.utc)
    db.flush()


def revoke_token_family(
        db: Session,
        family_id: str,
) -> None:
    """Revoke all active refresh tokens belonging to a token family."""

    now = datetime.now(timezone.utc)

    db.query(RefreshToken).filter(
        RefreshToken.family_id == family_id,
        RefreshToken.revoked_at.is_(None),
        ).update(
            {RefreshToken.revoked_at: now},
            synchronize_session="fetch",
        )

    db.flush()


def validate_refresh_token(
    db: Session,
    token: str,
) -> tuple[dict, RefreshToken]:
    """Validate the database session against its database record."""

    # Decode and validate the JWT.
    payload = decode_refresh_token(token)

    # Find its database record.
    token_record = get_refresh_token_record(db, token)

    if token_record is None:
        raise ValueError("Refresh token not found.")

    # Verify that the JWT claims match the database record.
    if (
        token_record.jti != payload["jti"] 
        or str(token_record.user_id) != payload["sub"]
    ):
        raise ValueError("Refresh token does not match its record.")

    # Verify database expiration.
    now = datetime.now(timezone.utc)
    expires_at = token_record.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:        
        raise ValueError("Refresh token has expired.")

    # Reject revoked tokens.
    if token_record.revoked_at is not None:
        raise RefreshTokenReuseError(token_record.family_id)

    return payload, token_record


def get_active_user(
    db: Session,
    user_id: int,
) -> User:
    """Retrive an active user by ID."""

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found.")

    if not user.is_active:
        raise ValueError("User account is inactive.")

    return user


def rotate_refresh_token(
        db: Session,
        token: str,
) -> tuple[User, str]:
    """Validate a refresh token, revoke it and issue a replacement."""

    try:
        # The JWT and its database record must be both valid before rotation ca proceed.
        payload, token_record = validate_refresh_token(db, token)

        try:
            # Check whether the user is active.
            user = get_active_user(db, int(payload["sub"]))
        except ValueError:
            family_id = token_record.family_id
            db.rollback()

            revoke_token_family(
                db,
                family_id,
            )

            db.commit()
            raise

        # Automatically revoke the old token.
        result = db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.id == token_record.id,
                RefreshToken.revoked_at.is_(None),)
            .values(revoked_at=datetime.now(timezone.utc))
        )

        # Another request may have already rotated this token.
        if result.rowcount != 1:
            raise RefreshTokenReuseError(token_record.family_id)

        # Issue a replacement in the same token family.
        new_refresh_token = create_and_store_refresh_token(
            db=db,
            user_id=user.id,
            family_id=token_record.family_id,
        )

        db.commit()

        return user, new_refresh_token
    
    except RefreshTokenReuseError as exc:
        db.rollback()

        # Revoke every remaining token in this family.
        revoke_token_family(db, exc.family_id)
        db.commit()

        raise

    except Exception:
        db.rollback()
        raise