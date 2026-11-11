import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.contact import ContactMessage as ContactMessageModel
from app.schemas.contact import ContactMessage, ContactResponse
from app.schemas.error import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/contact",
    tags=["Contact"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
        "/",
        status_code=status.HTTP_201_CREATED,
        response_model=ContactResponse,
        summary="Submit a contact form",
        description=(
            "Submit a contact form message. "
            "The message is validated and stored in the database. "
            "Authentication is not required. "
        ),
        response_description="Confirmation that the contact message was received",
        responses={
            500: {
                "model": ErrorResponse,
                "description": "Failed to save the contact message.",
            },
        },
    )
def submit_contact(
    message: ContactMessage,
    db: DatabaseSession,
    ):

    contact_message = ContactMessageModel(
        name = message.name,
        email= str(message.email),
        message = message.message,
    )

    try:
        db.add(contact_message)
        db.commit()
        db.refresh(contact_message)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to save contact message.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save contact message. Please try again.",
        ) from exc

    return {
        "success": True,
        "message": "Contact message received successfully.",
        "data": message,
    }