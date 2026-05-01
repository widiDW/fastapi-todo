from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.chapter import Chapter, Lesson
from app.models.user import User
from app.schemas.chapter import ChapterCreate, ChapterResponse, LessonCreate, LessonResponse
from app.core.security import get_current_user

router = APIRouter()

def check_course_owner(course_id: int, db: Session, current_user: User):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail="Not your course")
    return db_course

# CHAPTER
@router.post("/courses/{course_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(
    course_id: int,
    chapter: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_course_owner(course_id, db, current_user)
    new_chapter = Chapter(**chapter.dict(), course_id=course_id)
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    return new_chapter

# LESSON
@router.post("/chapters/{chapter_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    chapter_id: int,
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    check_course_owner(db_chapter.course_id, db, current_user)

    new_lesson = Lesson(**lesson.dict(), chapter_id=chapter_id)
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson