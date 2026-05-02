from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.enrollment import Enrollment
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import get_password_hash, get_current_user, require_student
from app.schemas.course import CourseOut
from app.core.deps import require_role

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user.password)
    
    new_user = User(
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url if hasattr(user, 'avatar_url') else None,
        hashed_password=hashed_pw,
        role="student"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=list[UserResponse]) # <- harus pake UserResponse
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("superadmin"))
):
    users = db.query(User).all()
    return users

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

from app.core.deps import require_role

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate, # schema tanpa password + role
    db: Session = Depends(get_db),
    _: User = Depends(require_role("superadmin")) # <- cuma superadmin
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # update field yang boleh diupdate
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("superadmin")) # <- cuma superadmin
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return