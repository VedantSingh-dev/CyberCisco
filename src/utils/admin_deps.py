from fastapi import Depends, HTTPException, status
from src.modals.user_models import User, UserRole
from src.utils.auth_deps import get_current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this resource",
        )
    return current_user