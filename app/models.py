from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    work_records = relationship("WorkRecord", back_populates="user", cascade="all, delete-orphan")


class WorkRecord(Base):
    __tablename__ = "work_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    record_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    customer_name = Column(String(200), nullable=False)
    work_content = Column(Text, nullable=False)
    work_type = Column(String(100), nullable=False, default="一般")
    status = Column(String(50), nullable=False, default="未対応")
    duration_minutes = Column(Integer, nullable=False, default=0)
    note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="work_records")
