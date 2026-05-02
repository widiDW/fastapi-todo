from pydantic import BaseModel
from typing import List, Optional


# Lesson
class LessonBase(BaseModel):
    title: str
    video_url: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = 0

class LessonCreate(LessonBase):
    pass

class LessonResponse(LessonBase):
    id: int
    chapter_id: int
    class Config:
        from_attributes = True
        
# Chapter
class ChapterBase(BaseModel):
    title: str
    order: Optional[int] = 0

class ChapterCreate(ChapterBase):
    pass

class ChapterResponse(ChapterBase):
    id: int
    course_id: int
    lessons: List[LessonResponse] = []
    class Config:
        from_attributes = True
