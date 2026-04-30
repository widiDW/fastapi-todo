from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseResponse

router = APIRouter()

@router.post("/courses", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    # instructor_id = 1 hardcode dulu, nanti ganti pake JWT
    new_course = Course(**course.dict(), instructor_id=1)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/courses", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()