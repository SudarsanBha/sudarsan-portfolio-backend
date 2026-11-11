from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime

class ContactMessage(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=2000)

    @field_validator("name", "message")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty or whitespace only.")

        return value


class ContactResponse(BaseModel):
    success: bool
    message: str
    data: ContactMessage


class ContactMessageRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    message: str
    created_at: datetime