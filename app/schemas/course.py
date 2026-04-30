from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[int] = 0
    thumbnail_url: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    slug: str
    instructor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True