from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from slugify import slugify
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user # UDAH GUA BENERIN

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.post("/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Only instructors or admins can create courses")

    course_slug = slugify(course.title)
    db_course = db.query(models.Course).filter(models.Course.slug == course_slug).first()
    if db_course:
        raise HTTPException(status_code=400, detail="Course title already exists")

    new_course = models.Course(
        **course.dict(),
        slug=course_slug,
        instructor_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/", response_model=List[schemas.CourseResponse])
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(models.Course).all()
    return courses