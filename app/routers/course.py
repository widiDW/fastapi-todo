from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.core.deps import require_role, get_current_user
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get(
    "/",
    response_model=List[CourseResponse],
    summary="Get all courses",
    description="Public: anyone can see published courses. Use?published=true to filter.",
    operation_id="get_all_courses"
)
def get_courses(
    db: Session = Depends(get_db),
    published: bool = Query(True, description="Filter by published status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    return db.query(Course).filter(Course.is_published == published).offset(skip).limit(limit).all()

@router.get(
    "/instructor/my-courses",
    response_model=List[CourseResponse],
    summary="Get my courses",
    description="Instructor only: get courses created by the logged-in instructor",
    operation_id="get_instructor_courses"
)
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    return db.query(Course).filter(Course.instructor_id == current_user.id).all()

@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Get course by ID",
    description="Student: must be enrolled. Instructor/Admin: can access any.",
    operation_id="get_course_by_id"
)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found"})

    # Role check: student must be enrolled
    if current_user.role == "student":
        is_enrolled = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()
        if not is_enrolled:
            raise HTTPException(
                status_code=403,
                detail={"error": "You must enroll to access this course"}
            )

    return course

@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
    description="Instructor/Admin only",
    operation_id="create_course"
)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    new_course = Course(**course_data.dict(), instructor_id=current_user.id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Update course",
    description="Only the instructor who owns the course or Admin",
    operation_id="update_course"
)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found"})

    if course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail={"error": "You don't own this course"})

    for key, value in course_data.dict(exclude_unset=True).items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course

@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete course",
    description="Only the instructor who owns the course or Admin",
    operation_id="delete_course"
)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("instructor", "admin"))
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found"})

    if course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail={"error": "You don't own this course"})

    db.delete(course)
    db.commit()
    return