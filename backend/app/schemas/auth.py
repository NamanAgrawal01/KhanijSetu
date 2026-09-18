from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str

class DemoLoginRequest(BaseModel):
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    designation: str = ""
    phone: str = ""
    subsidiary_id: Optional[int] = None
    mine_id: Optional[int] = None
    is_active: bool = True
    avatar_url: str = ""
    accessible_modules: list[str] = []

    class Config:
        from_attributes = True

TokenResponse.model_rebuild()
