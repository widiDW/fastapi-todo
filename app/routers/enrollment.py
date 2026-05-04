from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Enrollment, Course, User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut
from app.auth import get_current_user

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("", response_model=EnrollmentOut)
def enroll_course(
    enrollment_data: EnrollmentCreate, # <- cuma kirim course_id
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Cek course ada + published
    course = db.query(Course).filter(
        Course.id == enrollment_data.course_id, 
        Course.published == True
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail={"error": "Course not found or not published"})

    # Cek udah enroll belum
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == enrollment_data.course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "Already enrolled"})

    # Create enrollment, user_id ambil dari token
    new_enroll = Enrollment(
        user_id=current_user.id, # <- dari JWT, bukan dari body
        course_id=enrollment_data.course_id,
        status="active"
    )
    db.add(new_enroll)
    db.commit()
    db.refresh(new_enroll)
    return new_enroll


@router.get("/me", response_model=list[EnrollmentOut])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lihat semua course yang lu ikutin"""
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()
    return enrollments


@router.delete("/{course_id}")
def unenroll_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batalin enrollment"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail={"error": "Enrollment not found"})
    
    db.delete(enrollment)
    db.commit()
    return {"message": "Unenrolled successfully"}