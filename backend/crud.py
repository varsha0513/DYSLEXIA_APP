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
        """Update user profile"""
        db_user = UserCRUD.get_user_by_id(db, user_id)
        if db_user:
            update_data = user_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user and all related data"""
        db_user = UserCRUD.get_user_by_id(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False


# ================== Assessment Operations ==================

class AssessmentCRUD:
    @staticmethod
    def create_assessment(
        db: Session,
        user_id: int,
        assessment_data: schemas.AssessmentCreate
    ) -> Assessment:
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
    def get_user_assessments(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Assessment]:
        """Get all assessments for a user"""
        return db.query(Assessment).filter(
            Assessment.user_id == user_id
        ).offset(skip).limit(limit).order_by(
            desc(Assessment.assessment_date)
        ).all()

    @staticmethod
    def get_user_assessments_count(db: Session, user_id: int) -> int:
        """Get count of assessments for a user"""
        return db.query(Assessment).filter(
            Assessment.user_id == user_id
        ).count()


# ================== Assessment Result Operations ==================

class ResultCRUD:
    @staticmethod
    def create_result(
        db: Session,
        assessment_id: int,
        result_data: schemas.AssessmentResultCreate
    ) -> AssessmentResult:
        """Create assessment result"""
        db_result = AssessmentResult(
            assessment_id=assessment_id,
            **result_data.dict()
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def get_result_by_assessment(db: Session, assessment_id: int) -> Optional[AssessmentResult]:
        """Get result for assessment"""
        return db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id
        ).first()

    @staticmethod
    def get_user_average_wpm(db: Session, user_id: int) -> Optional[float]:
        """Get user's average WPM"""
        result = db.query(func.avg(AssessmentResult.wpm)).join(
            Assessment
        ).filter(Assessment.user_id == user_id).scalar()
        return round(result, 2) if result else None

    @staticmethod
    def get_user_average_accuracy(db: Session, user_id: int) -> Optional[float]:
        """Get user's average accuracy"""
        result = db.query(func.avg(AssessmentResult.accuracy_percent)).join(
            Assessment
        ).filter(Assessment.user_id == user_id).scalar()
        return round(result, 2) if result else None

    @staticmethod
    def get_user_latest_risk_score(db: Session, user_id: int) -> Optional[float]:
        """Get user's latest risk score"""
        result = db.query(AssessmentResult).join(
            Assessment
        ).filter(
            Assessment.user_id == user_id
        ).order_by(
            desc(AssessmentResult.created_at)
        ).first()
        return result.risk_score if result else None


# ================== Pronunciation Operations ==================

class PronunciationCRUD:
    @staticmethod
    def create_attempt(
        db: Session,
        user_id: int,
        attempt_data: schemas.PronunciationAttemptCreate
    ) -> PronunciationAttempt:
        """Create pronunciation attempt"""
        db_attempt = PronunciationAttempt(
            user_id=user_id,
            **attempt_data.dict()
        )
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        return db_attempt

    @staticmethod
    def get_user_word_attempts(
        db: Session,
        user_id: int,
        word: str
    ) -> List[PronunciationAttempt]:
        """Get all attempts for a word by user"""
        return db.query(PronunciationAttempt).filter(
            and_(
                PronunciationAttempt.user_id == user_id,
                PronunciationAttempt.word == word
            )
        ).order_by(
            desc(PronunciationAttempt.created_at)
        ).all()

    @staticmethod
    def get_user_pronunciation_accuracy(db: Session, user_id: int) -> Optional[float]:
        """Get user's pronunciation accuracy percentage"""
        total = db.query(PronunciationAttempt).filter(
            PronunciationAttempt.user_id == user_id
        ).count()
        if total == 0:
            return None
        correct = db.query(PronunciationAttempt).filter(
            and_(
                PronunciationAttempt.user_id == user_id,
                PronunciationAttempt.is_correct == True
            )
        ).count()
        accuracy = (correct / total) * 100
        return round(accuracy, 2)


# ================== Progress Operations ==================

class ProgressCRUD:
    @staticmethod
    def create_or_update_weekly_progress(db: Session, user_id: int) -> ProgressHistory:
        """Create or update weekly progress"""
        # Get week start date (Monday)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # Check if already exists
        progress = db.query(ProgressHistory).filter(
            and_(
                ProgressHistory.user_id == user_id,
                ProgressHistory.period_date == week_start,
                ProgressHistory.period_type == 'week'
            )
        ).first()

        if not progress:
            progress = ProgressHistory(
                user_id=user_id,
                period_date=week_start,
                period_type='week'
            )

        # Calculate aggregates from assessments in this week
        assessments = db.query(Assessment).filter(
            and_(
                Assessment.user_id == user_id,
                Assessment.assessment_date >= week_start
            )
        ).all()

        progress.total_assessments = len(assessments)

        if assessments:
            results = [a.results for a in assessments if a.results]
            if results:
                progress.avg_wpm = round(
                    sum(r.wpm for r in results) / len(results), 2
                )
                progress.avg_accuracy = round(
                    sum(r.accuracy_percent for r in results) / len(results), 2
                )
                progress.avg_risk_score = round(
                    sum(r.risk_score for r in results) / len(results), 2
                )

        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def get_user_progress_history(
        db: Session,
        user_id: int,
        weeks: int = 4
    ) -> List[ProgressHistory]:
        """Get user's progress for last N weeks"""
        start_date = datetime.now() - timedelta(weeks=weeks)
        return db.query(ProgressHistory).filter(
            and_(
                ProgressHistory.user_id == user_id,
                ProgressHistory.period_date >= start_date
            )
        ).order_by(
            desc(ProgressHistory.period_date)
        ).all()


# ================== Speed Trainer Operations ==================

class SpeedTrainerCRUD:
    @staticmethod
    def create_session(
        db: Session,
        user_id: Optional[int],
        session_data: schemas.SpeedTrainerSessionCreate
    ) -> SpeedTrainerSession:
        """Create speed trainer session"""
        db_session = SpeedTrainerSession(
            user_id=user_id,
            **session_data.dict()
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def mark_completed(db: Session, session_id: int) -> Optional[SpeedTrainerSession]:
        """Mark session as completed"""
        db_session = db.query(SpeedTrainerSession).filter(
            SpeedTrainerSession.id == session_id
        ).first()
        if db_session:
            db_session.is_completed = True
            db.commit()
            db.refresh(db_session)
        return db_session


# ================== Chunk Reading Operations ==================

class ChunkReadingCRUD:
    @staticmethod
    def create_session(
        db: Session,
        user_id: Optional[int],
        session_data: schemas.ChunkReadingSessionCreate
    ) -> ChunkReadingSession:
        """Create chunk reading session"""
        db_session = ChunkReadingSession(
            user_id=user_id,
            **session_data.dict()
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def mark_completed(db: Session, session_id: int) -> Optional[ChunkReadingSession]:
        """Mark session as completed"""
        db_session = db.query(ChunkReadingSession).filter(
            ChunkReadingSession.id == session_id
        ).first()
        if db_session:
            db_session.is_completed = True
            db.commit()
            db.refresh(db_session)
        return db_session
