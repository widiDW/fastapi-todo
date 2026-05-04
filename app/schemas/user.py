from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole
    
class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str