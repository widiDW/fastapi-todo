from fastapi import Depends, HTTPException, status
from typing import TYPE_CHECKING

# JANGAN IMPORT USER DI SINI LANGSUNG
if TYPE_CHECKING:
    from ..models.user import User

from .security import get_current_user  # atau dari mana get_current_user lu

def require_role(*allowed_roles: str):
    def role_checker(current_user = Depends(get_current_user)):  # pake type hint biasa aja
        # cek role pake getattr biar ga perlu import User
        user_role = getattr(current_user, "role", None)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Permission denied",
                    "required_roles": list(allowed_roles),
                    "your_role": user_role
                }
            )
        return current_user
    return role_checker