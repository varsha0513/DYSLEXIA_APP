"""
Pydantic validation schemas for request/response data
Data validation and serialization
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ================== User Schemas ==================

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str
    email: EmailStr
    password: str
    age: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating user data"""
    age: Optional[int] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    age: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserSignUp(BaseModel):
    """Schema for user sign up"""
    name: str
    email: EmailStr
    age: int
    password: str
    password_confirm: str


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str
    user: UserResponse


# ================== Assessment Schemas ==================

class AssessmentCreate(BaseModel):
    """Schema for creating an assessment"""
    paragraph_text: str
    recognized_text: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Schema for assessment response"""
    id: int
    user_id: int
    paragraph_text: str
    recognized_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Assessment Result Schemas ==================

class AssessmentResultCreate(BaseModel):
    """Schema for creating assessment results"""
    elapsed_time_seconds: float
    wpm: float
    spoken_words: int
    speed_category: Optional[str] = None
    total_words: int
    correct_words: int
    wrong_words: int
    missing_words: int
    extra_words: int
    accuracy_percent: float
    risk_score: float
    risk_level: str
    risk_indicators: Optional[list] = None
    accuracy_feedback: Optional[str] = None
    difficulty_assessment: Optional[str] = None
    recommendations: Optional[list] = None


class AssessmentResultResponse(BaseModel):
    """Schema for assessment result response"""
    id: int
    assessment_id: int
    elapsed_time_seconds: float
    wpm: float
    accuracy_percent: float
    risk_score: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Pronunciation Attempt Schemas ==================

class PronunciationAttemptCreate(BaseModel):
    """Schema for creating pronunciation attempt"""
    word: str
    attempt_number: int = 1
    recognized_text: Optional[str] = None
    is_correct: bool = False
    similarity_ratio: Optional[float] = None
    feedback: Optional[str] = None


class PronunciationAttemptResponse(BaseModel):
    """Schema for pronunciation attempt response"""
    id: int
    user_id: int
    word: str
    is_correct: bool
    similarity_ratio: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Pronunciation Check Schemas ==================

class PronunciationCheckCreate(BaseModel):
    """Schema for creating pronunciation check"""
    word: str
    spoken_word: Optional[str] = None
    is_correct: bool = False
    similarity_ratio: Optional[float] = None


class PronunciationCheckResponse(BaseModel):
    """Schema for pronunciation check response"""
    id: int
    word: str
    spoken_word: Optional[str] = None
    is_correct: bool
    similarity_ratio: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Progress History Schemas ==================

class ProgressHistoryCreate(BaseModel):
    """Schema for creating progress history"""
    average_accuracy: Optional[float] = None
    average_wpm: Optional[float] = None
    total_assessments: int = 1
    average_risk_score: Optional[float] = None


class ProgressHistoryResponse(BaseModel):
    """Schema for progress history response"""
    id: int
    user_id: int
    average_accuracy: Optional[float] = None
    average_wpm: Optional[float] = None
    total_assessments: int
    average_risk_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Speed Trainer Session Schemas ==================

class SpeedTrainerSessionCreate(BaseModel):
    """Schema for creating speed trainer session"""
    session_text: str
    total_words: int
    elapsed_time_seconds: Optional[float] = None
    calculated_wpm: Optional[float] = None


class SpeedTrainerSessionResponse(BaseModel):
    """Schema for speed trainer session response"""
    id: int
    session_text: str
    total_words: int
    calculated_wpm: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Chunk Reading Session Schemas ==================

class ChunkReadingSessionCreate(BaseModel):
    """Schema for creating chunk reading session"""
    session_text: str
    total_phrases: int
    total_words: int
    elapsed_time_seconds: Optional[float] = None
    calculated_wpm: Optional[float] = None
    phrases_per_second: Optional[float] = None


class ChunkReadingSessionResponse(BaseModel):
    """Schema for chunk reading session response"""
    id: int
    session_text: str
    total_phrases: int
    total_words: int
    calculated_wpm: Optional[float] = None
    phrases_per_second: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
