from app.models.notification import Notification


def create_notification(db, user_id: int, title: str, message: str):

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        status="UNREAD"
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
