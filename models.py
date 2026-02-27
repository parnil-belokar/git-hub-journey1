from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    area = Column(String, nullable=True)
    password = Column(String) # Stored as hashed
    is_active = Column(Boolean, default=True)

    complaints = relationship("Complaint", back_populates="reporter")

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    image_url = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String, default="Pending")
    issue_type = Column(String, nullable=True) # This is subcategory select
    department = Column(String, nullable=True)
    voice_url = Column(String, nullable=True)
    severity_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    department_suggested = Column(String, nullable=True)
    votes = Column(Integer, default=0)
    yes_votes = Column(Integer, default=0)
    no_votes = Column(Integer, default=0)
    idk_votes = Column(Integer, default=0)
    
    community_yes_ratio = Column(Float, default=0.5)
    critical_area_weight = Column(Float, default=0.3)
    department_urgency_index = Column(Float, default=0.5)
    priority_score = Column(Float, default=0.0)
    
    user_feedback = Column(String, nullable=True)
    user_feedback_rating = Column(Integer, nullable=True)
    estimated_completion_time = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reporter_id = Column(Integer, ForeignKey("users.id"))

    reporter = relationship("User", back_populates="complaints")

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    vote_type = Column(String(10)) # Yes, No, Idk

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    department = Column(String)
    status = Column(String)
    phone = Column(String)
    location = Column(String)
    rating = Column(Float)
    active_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
