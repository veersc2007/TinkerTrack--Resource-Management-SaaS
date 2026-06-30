from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, func
from app.database import Base


class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    status = Column(String(20), default="WAITING")  
    # WAITING → NOTIFIED → CANCELLED

    created_at = Column(DateTime, server_default=func.now())
