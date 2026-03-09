"""
Pydantic models for API request/response validation
Separate from SQLAlchemy models for data transfer
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ================== User Schemas ==================

class UserCreate(BaseModel):
    """Create new user"""
    username: str
    email: EmailStr
    age: Optional[int] = None


class UserUpdate(BaseModel):
    """Update user profile"""
    age: Optional[int] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    age: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy compatibility


# ================== Assessment Schemas ==================

class AssessmentCreate(BaseModel):
    """Create assessment"""
    paragraph_text: str
    recognized_text: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Assessment response"""
    id: int
    user_id: int
    paragraph_text: str
    recognized_text: Optional[str]
    assessment_date: datetime

    class Config:
        from_attributes = True


# ================== Assessment Result Schemas ==================

class AssessmentResultCreate(BaseModel):
    """Create assessment result"""
    elapsed_time_seconds: float
    wpm: float
    spoken_words: int
    total_words: int
    correct_words: int
    wrong_words: int
    missing_words: int
    extra_words: int
    accuracy_percent: float
    risk_score: float
    risk_level: str
    accuracy_feedback: Optional[str] = None
    difficulty_assessment: Optional[str] = None


class AssessmentResultResponse(BaseModel):
    """Assessment result response"""
    id: int
    assessment_id: int
    wpm: float
    accuracy_percent: float
    risk_score: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Pronunciation Schemas ==================

class PronunciationAttemptCreate(BaseModel):
    """Create pronunciation attempt"""
    word: str
    recognized_text: Optional[str] = None
    is_correct: bool
    similarity_ratio: Optional[float] = None
    feedback: Optional[str] = None


class PronunciationAttemptResponse(BaseModel):
    """Pronunciation attempt response"""
    id: int
    user_id: int
    word: str
    is_correct: bool
    similarity_ratio: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class PronunciationCheckCreate(BaseModel):
    """Create pronunciation check"""
    word: str
    recognized: Optional[str] = None
    is_correct: bool
    similarity_ratio: Optional[float] = None


class PronunciationCheckResponse(BaseModel):
    """Pronunciation check response"""
    id: int
    word: str
    recognized: Optional[str]
    is_correct: bool
    similarity_ratio: Optional[float]

    class Config:
        from_attributes = True


# ================== Progress Schemas ==================

class ProgressHistoryResponse(BaseModel):
    """Progress history response"""
    id: int
    user_id: int
    period_date: datetime
    total_assessments: int
    avg_wpm: Optional[float]
    avg_accuracy: Optional[float]
    improvement_percent: Optional[float]

    class Config:
        from_attributes = True


# ================== Speed Trainer Schemas ==================

class SpeedTrainerSessionCreate(BaseModel):
    """Create speed trainer session"""
    session_text: str
    total_words: int
    elapsed_time_seconds: float
    calculated_wpm: float


class SpeedTrainerSessionResponse(BaseModel):
    """Speed trainer session response"""
    id: int
    calculated_wpm: float
    elapsed_time_seconds: float
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Chunk Reading Schemas ==================

class ChunkReadingSessionCreate(BaseModel):
    """Create chunk reading session"""
    session_text: str
    total_phrases: int
    total_words: int
    elapsed_time_seconds: float
    calculated_wpm: float


class ChunkReadingSessionResponse(BaseModel):
    """Chunk reading session response"""
    id: int
    calculated_wpm: float
    elapsed_time_seconds: float
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ================== Aggregated Response Schemas ==================

class UserStatsResponse(BaseModel):
    """User statistics aggregated"""
    user: UserResponse
    total_assessments: int
    avg_wpm: Optional[float]
    avg_accuracy: Optional[float]
    latest_risk_score: Optional[float]
    improvement_trend: Optional[str]  # "improving", "stable", "declining"

    class Config:
        from_attributes = True


class AssessmentFullResponse(BaseModel):
    """Complete assessment with results"""
    assessment: AssessmentResponse
    results: Optional[AssessmentResultResponse]
    pronunciation_checks: List[PronunciationCheckResponse] = []

    class Config:
        from_attributes = True
