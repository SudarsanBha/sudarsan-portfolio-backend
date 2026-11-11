from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str = Field(min_length=1)