import logging

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.dependencies import require_roles
from app.models.users import User
from app.database import get_db
from app.models.contact import ContactMessage as ContactMessageModel
from app.schemas.contact import ContactMessageRecord
from app.schemas.error import ErrorResponse
from app.schemas.admin import AdminDashBoardResponse


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_roles("admin"))]

@router.get(
    "/dashboard",
    response_model=AdminDashBoardResponse,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required or access token invalid.",
        },
        403: {
            "model": ErrorResponse,
            "description": "Administrator privileges required.",
        },
    },
    summary="Get admin dashboard",
    description=(
        "Retrive dashboard information for the authenticated administrator. "
        "Requires a valid access token and the admin role."
    ),
    response_description="Administrator dashboard information.",
)
def admin_dashboard(
    current_user: AdminUser
):
    return {
        "message": "Welcome to the admin DashBoard",
        "admin_id": current_user.id,
        "admin_email": current_user.email,
       "role": current_user.role,
    }


@router.get(
    "/contact-messages",
    response_model=list[ContactMessageRecord],
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required or access token invalid.",
            },
        403: {
            "model": ErrorResponse,
            "description": "Administrator privileges required."
        },
        500: {
            "model": ErrorResponse,
            "description": "Failed to retrive contact messages.",
            },
    },
    summary="List all contact messages",
    description=(
        "Retrive all submitted contact messages, ordered from newest "
        "to oldest. Requires a valid access token and the admin role."
    ),
    response_description="A list of contact messages.",
)
def get_contact_messages(
    db: DatabaseSession,
    current_user : AdminUser,
):
    try:
        statement = select(ContactMessageModel).order_by(ContactMessageModel.created_at.desc())
        return db.scalars(statement).all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to retruve admin cotact messages.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrive contact messages. Please try again.",
        ) from exc