from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.core.deps import require_role
from app.core.security import get_password_hash

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Super Admin & Admin only. Use pagination for performance.",
    operation_id="get_all_users"
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    return db.query(User).offset(skip).limit(limit).all()

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Super Admin & Admin only",
    operation_id="get_user_by_id"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    return user

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Super Admin & Admin only",
    operation_id="create_user_admin"
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin"))
):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "Email already registered"})

    hashed_password = get_password_hash(user_data.password)
    new_user = User(**user_data.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Super Admin & Admin only",
    operation_id="update_user_admin"
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})

    for key, value in user_data.dict(exclude_unset=True).items():
        if key == "password":
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Super Admin only",
    operation_id="delete_user_admin"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail={"error": "Cannot delete yourself"})

    db.delete(user)
    db.commit()
    return