from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import(
     OAuth2PasswordBearer,
     HTTPBearer,
     HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.security import decode_access_token

# FastAPI extracts the token from:
# Authorization: Bearer <access_token>

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,
)

bearer_scheme = HTTPBearer(
    scheme_name="Bearer Token",
    description="Paste Your JWT access Token Here.",
    auto_error=False,
)

def get_current_user(
        token: Annotated[str | None, Depends(oauth2_scheme)],
        bearer_credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
        db: Annotated[Session, Depends(get_db)],
) -> User:
    """Validate the JWT and retrive the current database user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit():
            raise credentials_exception

        user_id = int(subject)

    except(jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception from None

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return user


def require_roles(*allowed_roles: str):
    """Create a dependency that only allows specified roles """
    if not allowed_roles:
        raise ValueError("At least one allowed role must be specified")

    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you do not have permisiion to perform this action"
            )
        return current_user

    return role_checker