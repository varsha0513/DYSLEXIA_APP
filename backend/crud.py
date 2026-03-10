"""
CRUD operations for database models
Data Access Layer (DAL) for the application
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from typing import List, Optional

from models import (
    User, Assessment, AssessmentResult, PronunciationAttempt,
    PronunciationCheck, ProgressHistory, SpeedTrainerSession,
    ChunkReadingSession
)
import schemas


# ================== User Operations ==================

class UserCRUD:
    @staticmethod
    def create_user(db: Session, user_data: schemas.UserCreate) -> User:
        """Create new user"""
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            age=user_data.age
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate) -> Optional[User]:
        """Update user data"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            if user_data.age is not None:
                db_user.age = user_data.age
            if user_data.email is not None:
                db_user.email = user_data.email
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False


# ================== Assessment Operations ==================

class AssessmentCRUD:
    @staticmethod
    def create_assessment(db: Session, user_id: int, assessment_data: schemas.AssessmentCreate) -> Assessment:
        """Create new assessment"""
        db_assessment = Assessment(
            user_id=user_id,
            paragraph_text=assessment_data.paragraph_text,
            recognized_text=assessment_data.recognized_text
        )
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        return db_assessment

    @staticmethod
    def get_assessment_by_id(db: Session, assessment_id: int) -> Optional[Assessment]:
        """Get assessment by ID"""
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()

    @staticmethod
    def get_user_assessments(db: Session, user_id: int, limit: int = 10) -> List[Assessment]:
        """Get user's assessments"""
        return db.query(Assessment).filter(
            Assessment.user_id == user_id
        ).order_by(desc(Assessment.created_at)).limit(limit).all()

    @staticmethod
    def delete_assessment(db: Session, assessment_id: int) -> bool:
        """Delete assessment"""
        db_assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if db_assessment:
            db.delete(db_assessment)
            db.commit()
            return True
        return False


# ================== Assessment Result Operations ==================

class ResultCRUD:
    @staticmethod
    def create_result(db: Session, assessment_id: int, result_data: schemas.AssessmentResultCreate) -> AssessmentResult:
        """Create assessment result"""
        db_result = AssessmentResult(
            assessment_id=assessment_id,
            elapsed_time_seconds=result_data.elapsed_time_seconds,
            wpm=result_data.wpm,
            spoken_words=result_data.spoken_words,
            speed_category=result_data.speed_category,
            total_words=result_data.total_words,
            correct_words=result_data.correct_words,
            wrong_words=result_data.wrong_words,
            missing_words=result_data.missing_words,
            extra_words=result_data.extra_words,
            accuracy_percent=result_data.accuracy_percent,
            risk_score=result_data.risk_score,
            risk_level=result_data.risk_level,
            risk_indicators=result_data.risk_indicators,
            accuracy_feedback=result_data.accuracy_feedback,
            difficulty_assessment=result_data.difficulty_assessment,
            recommendations=result_data.recommendations
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def get_result_by_assessment(db: Session, assessment_id: int) -> Optional[AssessmentResult]:
        """Get result by assessment ID"""
        return db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id
        ).first()

    @staticmethod
    def get_user_results(db: Session, user_id: int, limit: int = 10) -> List[AssessmentResult]:
        """Get all results for a user"""
        return db.query(AssessmentResult).join(
            Assessment
        ).filter(
            Assessment.user_id == user_id
        ).order_by(desc(AssessmentResult.created_at)).limit(limit).all()


# ================== Pronunciation Attempt Operations ==================

class PronunciationCRUD:
    @staticmethod
    def create_attempt(db: Session, user_id: int, attempt_data: schemas.PronunciationAttemptCreate) -> PronunciationAttempt:
        """Create pronunciation attempt"""
        db_attempt = PronunciationAttempt(
            user_id=user_id,
            word=attempt_data.word,
            attempt_number=attempt_data.attempt_number,
            recognized_text=attempt_data.recognized_text,
            is_correct=attempt_data.is_correct,
            similarity_ratio=attempt_data.similarity_ratio,
            feedback=attempt_data.feedback
        )
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        return db_attempt

    @staticmethod
    def get_word_attempts(db: Session, user_id: int, word: str) -> List[PronunciationAttempt]:
        """Get all attempts for a specific word by user"""
        return db.query(PronunciationAttempt).filter(
            and_(
                PronunciationAttempt.user_id == user_id,
                PronunciationAttempt.word == word
            )
        ).order_by(desc(PronunciationAttempt.created_at)).all()

    @staticmethod
    def get_user_pronunciation_history(db: Session, user_id: int, limit: int = 20) -> List[PronunciationAttempt]:
        """Get user's pronunciation history"""
        return db.query(PronunciationAttempt).filter(
            PronunciationAttempt.user_id == user_id
        ).order_by(desc(PronunciationAttempt.created_at)).limit(limit).all()

    @staticmethod
    def create_check(db: Session, assessment_id: int, check_data: schemas.PronunciationCheckCreate) -> PronunciationCheck:
        """Create pronunciation check"""
        db_check = PronunciationCheck(
            assessment_id=assessment_id,
            word=check_data.word,
            spoken_word=check_data.spoken_word,
            is_correct=check_data.is_correct,
            similarity_ratio=check_data.similarity_ratio
        )
        db.add(db_check)
        db.commit()
        db.refresh(db_check)
        return db_check

    @staticmethod
    def get_assessment_checks(db: Session, assessment_id: int) -> List[PronunciationCheck]:
        """Get pronunciation checks for an assessment"""
        return db.query(PronunciationCheck).filter(
            PronunciationCheck.assessment_id == assessment_id
        ).all()


# ================== Progress History Operations ==================

class ProgressCRUD:
    @staticmethod
    def create_progress(db: Session, user_id: int, progress_data: schemas.ProgressHistoryCreate) -> ProgressHistory:
        """Create progress history entry"""
        db_progress = ProgressHistory(
            user_id=user_id,
            average_accuracy=progress_data.average_accuracy,
            average_wpm=progress_data.average_wpm,
            total_assessments=progress_data.total_assessments,
            average_risk_score=progress_data.average_risk_score
        )
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress

    @staticmethod
    def create_or_update_weekly_progress(db: Session, user_id: int) -> ProgressHistory:
        """Create or update weekly progress"""
        now = datetime.utcnow()
        week_number = now.isocalendar()[1]
        year = now.year

        db_progress = db.query(ProgressHistory).filter(
            and_(
                ProgressHistory.user_id == user_id,
                ProgressHistory.week_number == week_number,
                ProgressHistory.year == year
            )
        ).first()

        # Get all assessments from past week
        week_ago = now - timedelta(days=7)
        assessments = db.query(AssessmentResult).join(
            Assessment
        ).filter(
            and_(
                Assessment.user_id == user_id,
                AssessmentResult.created_at >= week_ago
            )
        ).all()

        if not assessments:
            return db_progress

        avg_accuracy = sum(a.accuracy_percent for a in assessments) / len(assessments)
        avg_wpm = sum(a.wpm for a in assessments) / len(assessments)
        avg_risk = sum(a.risk_score for a in assessments) / len(assessments)

        if db_progress:
            db_progress.average_accuracy = avg_accuracy
            db_progress.average_wpm = avg_wpm
            db_progress.total_assessments = len(assessments)
            db_progress.average_risk_score = avg_risk
            db.commit()
        else:
            db_progress = ProgressHistory(
                user_id=user_id,
                week_number=week_number,
                year=year,
                average_accuracy=avg_accuracy,
                average_wpm=avg_wpm,
                total_assessments=len(assessments),
                average_risk_score=avg_risk
            )
            db.add(db_progress)
            db.commit()

        db.refresh(db_progress)
        return db_progress

    @staticmethod
    def get_user_progress(db: Session, user_id: int, limit: int = 12) -> List[ProgressHistory]:
        """Get user's progress history"""
        return db.query(ProgressHistory).filter(
            ProgressHistory.user_id == user_id
        ).order_by(desc(ProgressHistory.created_at)).limit(limit).all()


# ================== Speed Trainer Operations ==================

class SpeedTrainerCRUD:
    @staticmethod
    def create_session(db: Session, session_data: schemas.SpeedTrainerSessionCreate, user_id: Optional[int] = None) -> SpeedTrainerSession:
        """Create speed trainer session"""
        db_session = SpeedTrainerSession(
            user_id=user_id,
            session_text=session_data.session_text,
            total_words=session_data.total_words,
            elapsed_time_seconds=session_data.elapsed_time_seconds,
            calculated_wpm=session_data.calculated_wpm
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_session_by_id(db: Session, session_id: int) -> Optional[SpeedTrainerSession]:
        """Get speed trainer session by ID"""
        return db.query(SpeedTrainerSession).filter(SpeedTrainerSession.id == session_id).first()

    @staticmethod
    def get_user_sessions(db: Session, user_id: int, limit: int = 10) -> List[SpeedTrainerSession]:
        """Get user's speed trainer sessions"""
        return db.query(SpeedTrainerSession).filter(
            SpeedTrainerSession.user_id == user_id
        ).order_by(desc(SpeedTrainerSession.created_at)).limit(limit).all()


# ================== Chunk Reading Operations ==================

class ChunkReadingCRUD:
    @staticmethod
    def create_session(db: Session, session_data: schemas.ChunkReadingSessionCreate, user_id: Optional[int] = None) -> ChunkReadingSession:
        """Create chunk reading session"""
        db_session = ChunkReadingSession(
            user_id=user_id,
            session_text=session_data.session_text,
            total_phrases=session_data.total_phrases,
            total_words=session_data.total_words,
            elapsed_time_seconds=session_data.elapsed_time_seconds,
            calculated_wpm=session_data.calculated_wpm,
            phrases_per_second=session_data.phrases_per_second
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_session_by_id(db: Session, session_id: int) -> Optional[ChunkReadingSession]:
        """Get chunk reading session by ID"""
        return db.query(ChunkReadingSession).filter(ChunkReadingSession.id == session_id).first()

    @staticmethod
    def get_user_sessions(db: Session, user_id: int, limit: int = 10) -> List[ChunkReadingSession]:
        """Get user's chunk reading sessions"""
        return db.query(ChunkReadingSession).filter(
            ChunkReadingSession.user_id == user_id
        ).order_by(desc(ChunkReadingSession.created_at)).limit(limit).all()
