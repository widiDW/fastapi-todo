from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from..db.database import get_db
from..models.enrollment import Enrollment
from..models.course import Course
from..core.deps import require_role, get_current_user
from..models.user import User

router = APIRouter(prefix="/api/v1/enrollments", tags=["Enrollments"])

@router.post(
    "/{course_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Enroll to course",
    description="Student only: enroll to a published course",
    operation_id="enroll_to_course"
)
def enroll_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student"))
):
    course = db.query(Course).filter(Course.id == course_id, Course.is_published == True).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found or not published"})

    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "You are already enrolled"})

    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    return {"message": f"Successfully enrolled to {course.title}"}