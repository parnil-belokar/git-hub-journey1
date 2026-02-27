from typing import Optional, List
from pydantic import BaseModel
import datetime

class UserBase(BaseModel):
    phone_number: str

class UserCreate(UserBase):
    name: str
    password: str
    area: Optional[str] = None

class User(UserBase):
    id: int
    name: Optional[str] = None
    area: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: Optional[str] = None

class VoteCreate(BaseModel):
    vote_type: str

class ComplaintBase(BaseModel):
    title: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Assuming user uploads file, API will handle it and return URL, or they send URL directly
    image_url: str 
    
class ComplaintCreate(ComplaintBase):
    department: str
    subcategory: str # This maps to issue_type in DB
    voice_url: Optional[str] = None
    force_create: bool = False

class ComplaintAIResponse(ComplaintBase):
    id: int
    status: str
    created_at: datetime.datetime
    reporter_id: int
    department: Optional[str] = None
    voice_url: Optional[str] = None
    issue_type: Optional[str] = None # This is subcategory select
    severity_score: Optional[float] = None
    confidence_score: Optional[float] = None
    department_suggested: Optional[str] = None
    votes: int = 0
    yes_votes: int = 0
    no_votes: int = 0
    idk_votes: int = 0
    
    community_yes_ratio: float = 0.5
    critical_area_weight: float = 0.3
    department_urgency_index: float = 0.5
    priority_score: float = 0.0
    
    user_feedback: Optional[str] = None
    user_feedback_rating: Optional[int] = None
    estimated_completion_time: Optional[str] = None

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    issueCategory: str
    department: str
    subType: str
    severity: int
    confidence: int
    autoSelected: bool

class FeedbackCreate(BaseModel):
    feedback: str
    rating: int

class Worker(BaseModel):
    id: int
    name: str
    department: str
    status: str
    phone: str
    location: str
    rating: float
    active_tasks: int
    completed_tasks: int

    class Config:
        from_attributes = True
