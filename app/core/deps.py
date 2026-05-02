from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.core.security import get_current_user

def require_role(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles and current_user.role!= "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker