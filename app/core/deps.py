from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import User

ROLE_HIERARCHY = {
    "student": 0,
    "instructor": 1,
    "admin": 2,
    "super_admin": 3  # <- PALING TINGGI
}

def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_role = current_user.role
        user_level = ROLE_HIERARCHY.get(user_role, -1)
        
        # DAPETIN LEVEL MINIMAL YANG DIBUTUHKAN
        min_required_level = min([ROLE_HIERARCHY.get(r, 999) for r in allowed_roles])
        
        # SUPER_ADMIN BISA LAKUIN APA AJA
        if user_level >= min_required_level or user_role == "super_admin":
            return current_user
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Permission denied",
                "required_roles": list(allowed_roles),
                "your_role": user_role
            }
        )
    return role_checker