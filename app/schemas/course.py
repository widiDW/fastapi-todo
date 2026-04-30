from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Schema buat bikin course baru
class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    price: int = Field(default=0, ge=0) # ge=0 artinya ga boleh minus
    thumbnail_url: Optional[str] = None

# Schema buat response ke user
class CourseResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    price: int
    thumbnail_url: Optional[str]
    instructor_id: int
    created_at: datetime

    class Config:
        from_attributes = True # Biar bisa convert dari SQLAlchemy model