"""
SQLAlchemy ORM Models for Dyslexia Assessment App
Database schema definition
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    Boolean, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from database import Base


# ================== User Models ==================

class User(Base):
    """User profile model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    assessments = relationship(
        "Assessment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    pronunciation_attempts = relationship(
        "PronunciationAttempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    progress_history = relationship(
        "ProgressHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# ================== Assessment Models ==================

class Assessment(Base):
    """Reading assessment session"""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paragraph_text = Column(Text, nullable=False)
    recognized_text = Column(Text, nullable=True)
    assessment_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="assessments")
    results = relationship(
        "AssessmentResult",
        back_populates="assessment",
        cascade="all, delete-orphan",
        uselist=False
    )
    pronunciation_checks = relationship(
        "PronunciationCheck",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Assessment(id={self.id}, user_id={self.user_id})>"


class AssessmentResult(Base):
    """Results of a single assessment"""
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id"),
        nullable=False,
        unique=True
    )

    # Speed metrics
    elapsed_time_seconds = Column(Float, nullable=False)
    wpm = Column(Float, nullable=False)
    spoken_words = Column(Integer, nullable=False)
    speed_category = Column(String(50), nullable=True)  # slow, normal, fast

    # Accuracy metrics
    total_words = Column(Integer, nullable=False)
    correct_words = Column(Integer, nullable=False)
    wrong_words = Column(Integer, nullable=False)
    missing_words = Column(Integer, nullable=False)
    extra_words = Column(Integer, nullable=False)
    accuracy_percent = Column(Float, nullable=False)

    # Risk assessment
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, moderate, high
    risk_indicators = Column(JSON, nullable=True)  # JSON array of indicators

    # Feedback
    accuracy_feedback = Column(Text, nullable=True)
    difficulty_assessment = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)  # JSON array

    # Metadata
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="results")

    def __repr__(self):
        return f"<AssessmentResult(assessment_id={self.assessment_id})>"


# ================== Pronunciation Training Models ==================

class PronunciationAttempt(Base):
    """Single pronunciation training attempt"""
    __tablename__ = "pronunciation_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word = Column(String(100), nullable=False, index=True)
    attempt_number = Column(Integer, default=1)
    recognized_text = Column(String(100), nullable=True)
    is_correct = Column(Boolean, default=False)
    similarity_ratio = Column(Float, nullable=True)  # 0.0 to 1.0
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="pronunciation_attempts")

    def __repr__(self):
        return f"<PronunciationAttempt(word='{self.word}')>"


class PronunciationCheck(Base):
    """Pronunciation check within an assessment"""
    __tablename__ = "pronunciation_checks"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    word = Column(String(100), nullable=False)
    recognized = Column(String(100), nullable=True)
    is_correct = Column(Boolean, default=False)
    similarity_ratio = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="pronunciation_checks")

    def __repr__(self):
        return f"<PronunciationCheck(word='{self.word}')>"


# ================== Progress Tracking Models ==================

class ProgressHistory(Base):
    """User progress over time"""
    __tablename__ = "progress_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Weekly/Monthly aggregated stats
    period_date = Column(DateTime, nullable=False, index=True)  # Week/Month start
    period_type = Column(String(10), nullable=False)  # 'week' or 'month'

    # Aggregated metrics
    total_assessments = Column(Integer, default=0)
    avg_wpm = Column(Float, nullable=True)
    avg_accuracy = Column(Float, nullable=True)
    avg_risk_score = Column(Float, nullable=True)
    improvement_percent = Column(Float, nullable=True)

    # Progress indicators
    words_practiced = Column(Integer, default=0)
    improvement_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress_history")

    def __repr__(self):
        return f"<ProgressHistory(user_id={self.user_id}, period={self.period_date})>"


class SpeedTrainerSession(Base):
    """Speed trainer session tracking"""
    __tablename__ = "speed_trainer_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional, can be anonymous
    session_text = Column(Text, nullable=False)
    session_date = Column(DateTime, server_default=func.now())

    # Results
    total_words = Column(Integer, nullable=False)
    elapsed_time_seconds = Column(Float, nullable=False)
    calculated_wpm = Column(Float, nullable=False)
    current_round = Column(Integer, default=0)
    total_rounds = Column(Integer, default=0)

    # Status
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<SpeedTrainerSession(wpm={self.calculated_wpm})>"


class ChunkReadingSession(Base):
    """Chunk/phrase reading session tracking"""
    __tablename__ = "chunk_reading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional
    session_text = Column(Text, nullable=False)
    session_date = Column(DateTime, server_default=func.now())

    # Results
    total_phrases = Column(Integer, nullable=False)
    total_words = Column(Integer, nullable=False)
    elapsed_time_seconds = Column(Float, nullable=False)
    calculated_wpm = Column(Float, nullable=False)
    phrases_per_second = Column(Float, nullable=True)

    # Status
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ChunkReadingSession(wpm={self.calculated_wpm})>"
