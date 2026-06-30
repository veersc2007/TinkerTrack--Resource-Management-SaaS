from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.schemas.user import (
    UserResponse,
    UserUpdate
)

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_admin
from app.auth.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["👤 Users"]
)

# --------------------------------------------------------
# GET ALL USERS (Admin Only)
# --------------------------------------------------------
@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    return db.query(User).all()


# --------------------------------------------------------
# GET USER BY ID
# --------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only owner or admin can view a profile
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return user


# --------------------------------------------------------
# UPDATE USER
# --------------------------------------------------------
@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    updated: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only owner or admin
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    if updated.name is not None:
        user.name = updated.name

    if updated.email is not None:
        user.email = updated.email

    if updated.password is not None:
        user.hashed_password = hash_password(updated.password)

    db.commit()
    db.refresh(user)

    return user


# --------------------------------------------------------
# DELETE USER
# --------------------------------------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only owner or admin
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }


# --------------------------------------------------------
# MAKE ADMIN (Admin Only)
# --------------------------------------------------------
@router.put("/{user_id}/make-admin")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = "admin"

    db.commit()
    db.refresh(user)

    return {
        "message": f"{user.name} has been promoted to admin."
    }

@router.get("/peak-hours")
def peak_hours(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        return {"detail": "Only admins can access analytics"}

    results = (
        db.query(
            func.extract("hour", Reservation.start_time).label("hour"),
            func.count(Reservation.id)
        )
        .group_by("hour")
        .order_by("hour")
        .all()
    )

    return [
        {"hour": int(r.hour), "bookings": r[1]}
        for r in results
    ]

@router.get("/user-activity")
def user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        return {"detail": "Only admins can access analytics"}

    results = (
        db.query(
            User.id,
            User.name,
            func.count(Reservation.id).label("total")
        )
        .join(Reservation, Reservation.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Reservation.id).desc())
        .all()
    )

    return [
        {"user_id": r.id, "name": r.name, "bookings": r.total}
        for r in results
    ]
