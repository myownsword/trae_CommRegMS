from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class ActivityStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class RegistrationStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    location = Column(String(300), nullable=False)
    start_time = Column(DateTime, nullable=False)
    max_participants = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    registrations = relationship("Registration", back_populates="activity")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    remark = Column(Text, nullable=True)
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    activity = relationship("Activity", back_populates="registrations")
