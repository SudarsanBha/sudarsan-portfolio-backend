import logging
import jwt

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

# from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.dependencies import get_current_user
from app.models.users import User
from app.schemas.user import(
    TokenResponse,
    UserRegister,
    UserLogin,
    UserResponse,
    RefreshTokenRequest,
)
from app.schemas.error import ErrorResponse
from app.security import(
    create_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

from app.services.refresh_tokens import (
    create_and_store_refresh_token,
    rotate_refresh_token,
    RefreshTokenReuseError,
    get_refresh_token_record,
    revoke_refresh_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

DatabaseSession = Annotated[Session, Depends(get_db)]

@router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            409: {
                "model": ErrorResponse,
                "description": "An account with this email is already exists.",
            },
            500: {
                "model": ErrorResponse,
                "description": "Database error during registration.",
            },
        },
        summary="Register a new user",
        description=(
            "Create a new user account with a full name, email address, "
            "and password. New accounts are assigned the user role by default."
        ),
        response_description="The newly registered user's information.",
    )


def register_user(
    data: UserRegister,
    db: DatabaseSession
):
    email = str(data.email).strip().lower()

    # print("Register Email:", repr(email))

    existing_user = db.query(User).filter(User.email == email).first()

    # print("Existing User:", repr(existing_user))
    # print("Existing User truth value:", bool(existing_user))

    if existing_user:
        # print("409 raised by existing-user check")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email is already exists.",
        )

    user = User(
        full_name = data.full_name.strip(),
        email = email,
        hashed_password = hash_password(data.password),
        role="user",
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError as exc:
        db.rollback()

        logger.warning(
             "Registration rejected due to a database uniqueness conflict."
        )

        # print("Intergrity error: ", repr(exc.orig))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration conflicts with an existing database record.",
        ) from None

    except SQLAlchemyError:
        db.rollback()

        logger.exception("Database error occured during user registration.")

        raise HTTPException(
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Unable to register user. Please try again.",
        ) from None
    return user

@router.post(
        "/login",
        response_model=TokenResponse,
        responses={
            401: {
                "model": ErrorResponse,
                "description": "Invalid email or assword.",
            },
            403: {
                "model": ErrorResponse,
                "description": "User account is inactive.",
            },
        },
        summary="Authenticate a user",
        description=(
            "Authenticate using an email address and password. "
            "Returns a JWT access token and a refresh token when "
            "the credentials are valid."
        ),
        response_description="JWT access token, refresh token, and token type.",
    )
def login_user(
    data: UserLogin,
    db: DatabaseSession
):
    email = str(data.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    token = create_access_token(
        subject = str(user.id),
        role = user.role,
    )

    try:
        refresh_token = create_and_store_refresh_token(
            db = db,
            user_id = user.id,
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()

        logger.exception("Database error occured during user login.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete login. Please try again."
        ) from None

    return TokenResponse(
        access_token=token,
        refresh_token=refresh_token,)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh authentication tokens",
    description=(
        "Exchange a valid refresh token for a new access token "
        "and a rotated refresh token."
    ),
)
def refresh_access_token(
    data: RefreshTokenRequest,
    db: DatabaseSession,
):
    try:
        user, new_refresh_token = rotate_refresh_token(
            db=db,
            token=data.refresh_token,
        )

        new_access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    except RefreshTokenReuseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected. Please log in again."
        ) from None

    except (ValueError, jwt.PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        ) from None

    except Exception:
        logger.exception("Unexpected error during token refresh.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to refresh authentication tokens."
        ) from None


@router.post(
        "/logout",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Log out an user",
        description="Revoke the submitted refresh token so it can not be used "
        "to obtain new access or refresh tokens. Existing access "
        "tokens remain valid until they expire.",
)
def logout_user(
    data: RefreshTokenRequest,
    db: DatabaseSession,
):
    try:
        payload = decode_refresh_token(data.refresh_token)
        token_record = get_refresh_token_record(
            db=db,
            token=data.refresh_token,
        )

        if token_record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        if (
            token_record.jti != payload["jti"]
            or str(token_record.user_id) != payload["sub"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token."
            )

        if token_record.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has already been revoked."
            )

        revoke_refresh_token(db, token_record)

        db.commit()

    except HTTPException:
        raise

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        ) from None

    except Exception:
        db.rollback()
        logger.exception("Unexpected error during logout.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to log out.",
        ) from None


@router.get(
        "/me",
        response_model=UserResponse,
        responses={
            401: {
                "model": ErrorResponse,
                "description": "Missing, invalid, or exired access token.",
            },
        },
        summary="Get current user",
        description=(
            "Retrive the profile information  of the currently authenticated user. "
            "Requires a valid JWT access token."
        ),
        response_description="The authenticated user's profile.",
    )
def read_current_user(
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        return current_user