from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, Enrollment
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, get_current_user, require_student
from app.schemas.course import CourseOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(**user.dict(exclude={"password"}), password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)): # UDAH BISA SEKARANG
    return current_user

@router.get("/me/courses", response_model=list[CourseOut])
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):
    # Ambil semua enrollment user + join data course nya
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).options(joinedload(Enrollment.course)).all()

    # Ambil object course aja dari enrollment
    courses = [enrollment.course for enrollment in enrollments]
    return courses