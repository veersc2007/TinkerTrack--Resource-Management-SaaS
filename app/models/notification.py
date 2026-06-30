from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(100), nullable=False)
    message = Column(String(255), nullable=False)

    status = Column(String(20), default="UNREAD")
    # UNREAD / READ

    created_at = Column(DateTime, server_default=func.now())
