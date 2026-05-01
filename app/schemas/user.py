from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = "student"
    avatar_url: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole
    
class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str