from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["🔔 Notifications"]
)

# ---------------------------------------------------
# GET MY NOTIFICATIONS
# ---------------------------------------------------
@router.get(
    "/",
    responses={
        200: {
            "description": "List of notifications",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "user_id": 2,
                            "title": "Reservation Created",
                            "message": "Your booking is confirmed",
                            "status": "UNREAD",
                            "created_at": "2026-01-10T10:00:00"
                        }
                    ]
                }
            }
        }
    }
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()


# ---------------------------------------------------
# MARK AS READ
# ---------------------------------------------------
@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.status = "READ"
    db.commit()

    return {"message": "Notification marked as read"}


# ---------------------------------------------------
# (OPTIONAL) ADMIN: GET ALL NOTIFICATIONS
# ---------------------------------------------------
@router.get("/all")
def get_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return db.query(Notification).all()
