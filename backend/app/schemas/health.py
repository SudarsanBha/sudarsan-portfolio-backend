from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(min_length=1)
    service: str = Field(min_length=1)