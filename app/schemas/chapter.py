from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChapterBase(BaseModel):
    title: str
    content: str
    order: int
    course_id: int

class ChapterCreate(ChapterBase):
    pass

class ChapterUpdate(BaseModel): # <- INI YANG KURANG
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None

class ChapterResponse(ChapterBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Pydantic v2