from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.core.deps import get_current_user, require_role

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
    current_user: User = Depends(get_current_user)
):
    """Update user - user can update self, admin/super_admin can update anyone"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cek permission: diri sendiri atau admin/super_admin
    if current_user.id!= user_id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Cegah non-super_admin ubah role jadi super_admin
    if user_update.role == "super_admin" and current_user.role!= "super_admin":
        raise HTTPException(status_code=403, detail="Cannot assign super_admin role")

    for key, value in user_update.dict(exclude_unset=True).items():
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
    """Delete user - admin/super_admin only with hierarchy check"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cegah hapus diri sendiri
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # HIERARCHY: super_admin bisa hapus semua
    # admin ga bisa hapus super_admin
    if user.role == "super_admin" and current_user.role!= "super_admin":
        raise HTTPException(status_code=403, detail="Cannot delete super_admin")

    # admin ga bisa hapus admin lain
    if user.role == "admin" and current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot delete another admin")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} deleted successfully"}