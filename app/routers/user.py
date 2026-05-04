from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.schemas.user import UserOut, UserUpdate
from app.core.deps import get_current_user, require_role
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    """Get all users - admin & super_admin only"""
    users = db.query(User).all()
    return users

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged in user"""
    return current_user

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cek permission: user biasa cuma bisa update dirinya sendiri
    if current_user.id != user_id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = user_update.model_dump(exclude_unset=True)

    # KHUS PASSWORD: HASH DULU SEBELUM SIMPAN
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]  # hapus password plain text

    # CEGAH NON SUPER_ADMIN UBAH ROLE JADI SUPER_ADMIN
    if "role" in update_data and update_data["role"] == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Cannot set role to super_admin")

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    if user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Cannot delete super_admin")

    try:
        if user.role in ["instructor", "admin", "super_admin"]:
            courses = db.query(Course).filter(Course.instructor_id == user_id).all()
            
            for course in courses:
                # 1. HAPUS LESSONS DULU - INI YANG KEMARIN KETINGGALAN
                chapters = db.query(Chapter).filter(Chapter.course_id == course.id).all()
                for chapter in chapters:
                    db.query(Lesson).filter(Lesson.chapter_id == chapter.id).delete()
                
                # 2. HAPUS CHAPTER
                db.query(Chapter).filter(Chapter.course_id == course.id).delete()
                
                # 3. HAPUS ENROLLMENT
                db.query(Enrollment).filter(Enrollment.course_id == course.id).delete()
                
                # 4. HAPUS COURSE
                db.delete(course)

        if user.role == "student":
            db.query(Enrollment).filter(Enrollment.user_id == user_id).delete()

        db.delete(user)
        db.commit()
        return {"message": f"User {user.email} and all related data deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")