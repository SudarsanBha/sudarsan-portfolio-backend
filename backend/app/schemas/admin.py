from pydantic import BaseModel, EmailStr

class AdminDashBoardResponse(BaseModel):
    message: str
    admin_id: int
    admin_email: EmailStr
    role: str