from fastapi import HTTPException, status

from app.models.user import User


def require_admin(current_user: User):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user
