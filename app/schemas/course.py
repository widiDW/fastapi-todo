from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[int] = 0
    thumbnail_url: Optional[str] = None

class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    price: int = 0
    thumbnail_url: str | None = None
    published: bool = False 

class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    thumbnail_url: str | None = None
    published: bool | None = None 

class CourseResponse(CourseBase):
    id: int
    slug: str
    instructor_id: int
    created_at: datetime
    updated_at: datetime
    
class CourseOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: float | None = None

    class Config:
        from_attributes = True