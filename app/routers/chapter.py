from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.chapter import Chapter
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse
from app.core.deps import require_role, get_current_user
from app.models.user import User

router = APIRouter(prefix="/chapters", tags=["Chapters"])

@router.get(
    "/course/{course_id}",
    response_model=List[ChapterResponse],
    summary="Get chapters by course",
    description="Student: must be enrolled. Instructor/Admin: can access any.",
    operation_id="get_chapters_by_course"
)
def get_chapters_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found"})

    # Student harus enroll dulu
    if current_user.role == "student":
        is_enrolled = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()
        if not is_enrolled:
            raise HTTPException(
                status_code=403,
                detail={"error": "Enroll to this course first to see chapters"}
            )

    return db.query(Chapter).filter(Chapter.course_id == course_id).order_by(Chapter.order).all()

@router.post(
    "/",
    response_model=ChapterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create chapter",
    description="Instructor/Admin only. Must own the course.",
    operation_id="create_chapter"
)
def create_chapter(
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    course = db.query(Course).filter(Course.id == chapter_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found"})

    # Cek ownership
    if course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail={"error": "You don't own this course"})

    new_chapter = Chapter(**chapter_data.dict())
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    return new_chapter

@router.put(
    "/{chapter_id}",
    response_model=ChapterResponse,
    summary="Update chapter",
    description="Only the instructor who owns the course or Admin",
    operation_id="update_chapter"
)
def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail={"error": "Chapter not found"})

    course = db.query(Course).filter(Course.id == chapter.course_id).first()
    if course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail={"error": "You don't own this course"})

    for key, value in chapter_data.dict(exclude_unset=True).items():
        setattr(chapter, key, value)

    db.commit()
    db.refresh(chapter)
    return chapter

@router.delete(
    "/{chapter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete chapter",
    description="Only the instructor who owns the course or Admin",
    operation_id="delete_chapter"
)
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail={"error": "Chapter not found"})

    course = db.query(Course).filter(Course.id == chapter.course_id).first()
    if course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail={"error": "You don't own this course"})

    db.delete(chapter)
    db.commit()
    return