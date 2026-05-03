from fastapi import Depends, HTTPException, status
from app.models.user import User
from. deps import get_current_user

def require_role(*allowed_roles: str):
    """
    Usage: Depends(require_role("instructor", "admin"))
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Permission denied",
                    "required_roles": list(allowed_roles),
                    "your_role": current_user.role
                }
            )
        return current_user
    return role_checker