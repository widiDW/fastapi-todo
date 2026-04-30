from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, Token, TokenRefresh
from app.auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, get_current_user, verify_refresh_token,
    get_current_admin_user
)

router = APIRouter(prefix="/user", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    return db.query(User).all()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email udah kepake Jhon")
    
    hashed_pw = get_password_hash(user.password)
    user_baru = User(
        nama=user.nama,
        email=user.email,
        umur=user.umur,
        hashed_password=hashed_pw,
        role=user.role
    )
    db.add(user_baru)
    db.commit()
    db.refresh(user_baru)
    return user_baru

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    # INI YANG GUA BENERIN
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah Jhon",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    payload = verify_refresh_token(token_data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token invalid")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User ga ketemu")
    
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.nama is not None:
        current_user.nama = user_update.nama
    if user_update.email is not None:
        current_user.email = user_update.email
    if user_update.umur is not None:
        current_user.umur = user_update.umur
    
    db.commit()
    db.refresh(current_user)
    return current_user


# GET USER - CUMA ADMIN
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nggak ketemu Jhon")
    
    # User biasa cuma boleh liat data sendiri
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Lu bukan admin Jhon")
    
    return user

# PUT USER - CUMA ADMIN
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nggak ketemu Jhon")
    
    # User biasa cuma boleh edit diri sendiri, admin bebas
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Ngapain edit user lain Jhon")
    
    # Update field yg dikirim aja
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Kalo ada password, hash dulu
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

# DELETE USER - CUMA ADMIN
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Pake yg admin
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nggak ketemu Jhon")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Haram hapus diri sendiri Jhon")
    
    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} berhasil dihapus Jhon"}