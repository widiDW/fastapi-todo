from fastapi import APIRouter, Depends, HTTPException, status # TAMBAH status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course # INI YG KETINGGALAN
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.core.security import get_current_user # INI JUGA
from typing import List

router = APIRouter()

@router.get("/instructor/courses", response_model=List[CourseResponse])
def get_my_instructor_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Cek role
    if current_user.role!= "instructor":
        raise HTTPException(status_code=403, detail="Only instructors can access this")

    # Query course milik instructor ini
    courses = db.query(Course).filter(Course.instructor_id == current_user.id).all()
    return courses

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    new_course = Course(**course.dict(), instructor_id=current_user.id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/courses", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail="Not your course")
    for key, value in course_data.dict(exclude_unset=True).items():
        setattr(db_course, key, value)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.instructor_id!= current_user.id and current_user.role!= "admin":
        raise HTTPException(status_code=403, detail="Not your course")
    db.delete(db_course)
    db.commit()
    return