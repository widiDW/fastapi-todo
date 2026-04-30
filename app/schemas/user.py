from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    nama: str
    email: EmailStr
    umur: int

# Buat register
class UserCreate(UserBase):
    password: str

# Buat update - INI YANG KURANG TADI
class UserUpdate(BaseModel):
    nama: Optional[str] = None
    email: Optional[EmailStr] = None
    umur: Optional[int] = None
    password: Optional[str] = None

# Buat response
class UserOut(UserBase):
    id: int
    role: str
    
    class Config:
        from_attributes = True

# Alias biar cocok sama router lu yg error
UserResponse = UserOut

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# Alias biar cocok sama router lu yg error
TokenRefresh = Token
RefreshTokenRequest = Token