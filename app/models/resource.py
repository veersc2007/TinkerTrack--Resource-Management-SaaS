from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean
from app.database import Base
approval_required = Column(Boolean, default=False)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(String(255))

    location = Column(String(100))

    status = Column(String(30), default="Available")

    reservations = relationship(
        "Reservation",
        back_populates="resource",
        cascade="all, delete"
    )
