"""SQLAlchemy implementation of ISessionRepository."""

from datetime import datetime, date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_, or_

from app.domains.scheduling.entities import Session
from app.domains.scheduling.repositories import ISessionRepository
from app.domains.scheduling.value_objects import SessionStatus
from app.infrastructure.persistence.sqlalchemy_models import Session as SessionModel
from app.infrastructure.persistence.mappers import SessionMapper


class SessionRepositoryImpl(ISessionRepository):
    """SQLAlchemy implementation of session repository."""

    def __init__(self, db: DBSession):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = SessionMapper()

    def save(self, session: Session) -> Session:
        """Save session (create or update)."""
        if session.id:
            # Update existing
            db_model = self.db.query(SessionModel).filter(
                SessionModel.id == session.id
            ).first()

            if db_model:
                self.mapper.update_orm(db_model, session)
                self.db.commit()
                self.db.refresh(db_model)
                return self.mapper.to_domain(db_model)

        # Create new
        db_model = self.mapper.to_orm(session)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self.mapper.to_domain(db_model)

    def get_by_id(self, session_id: int) -> Optional[Session]:
        """Get session by ID."""
        db_model = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()

        if db_model:
            return self.mapper.to_domain(db_model)
        return None

    def get_by_instructor(
        self,
        instructor_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """Get sessions for an instructor."""
        query = self.db.query(SessionModel).filter(
            SessionModel.instructor_id == instructor_id
        )

        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            query = query.filter(SessionModel.start_at >= start_dt)

        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time())
            query = query.filter(SessionModel.start_at <= end_dt)

        if status:
            query = query.filter(SessionModel.status == status.value)

        db_models = query.order_by(SessionModel.start_at).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_student(
        self,
        student_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """Get sessions for a student."""
        query = self.db.query(SessionModel).filter(
            SessionModel.student_id == student_id
        )

        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            query = query.filter(SessionModel.start_at >= start_dt)

        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time())
            query = query.filter(SessionModel.start_at <= end_dt)

        if status:
            query = query.filter(SessionModel.status == status.value)

        db_models = query.order_by(SessionModel.start_at).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[Session]:
        """Get all sessions for an instructor in a date range."""
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        db_models = self.db.query(SessionModel).filter(
            SessionModel.instructor_id == instructor_id,
            SessionModel.start_at >= start_dt,
            SessionModel.start_at <= end_dt
        ).order_by(SessionModel.start_at).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def get_upcoming_by_instructor(
        self,
        instructor_id: int,
        limit: int = 10
    ) -> List[Session]:
        """Get upcoming and in-progress sessions for an instructor.

        Shows sessions that:
        - Haven't ended yet (end_at > now)
        - Are confirmed or pending confirmation

        This includes both upcoming sessions AND sessions currently in progress.
        """
        now = datetime.utcnow()

        db_models = self.db.query(SessionModel).filter(
            SessionModel.instructor_id == instructor_id,
            SessionModel.end_at > now,  # Show until session ends
            SessionModel.status.in_([
                SessionStatus.PENDING_CONFIRMATION.value,
                SessionStatus.CONFIRMED.value
            ])
        ).order_by(SessionModel.start_at).limit(limit).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def get_upcoming_by_student(
        self,
        student_id: int,
        limit: int = 10
    ) -> List[Session]:
        """Get upcoming and in-progress sessions for a student.

        Shows sessions that:
        - Haven't ended yet (end_at > now)
        - Are confirmed or pending confirmation

        This includes both upcoming sessions AND sessions currently in progress.
        """
        now = datetime.utcnow()

        db_models = self.db.query(SessionModel).filter(
            SessionModel.student_id == student_id,
            SessionModel.end_at > now,  # Show until session ends
            SessionModel.status.in_([
                SessionStatus.PENDING_CONFIRMATION.value,
                SessionStatus.CONFIRMED.value
            ])
        ).order_by(SessionModel.start_at).limit(limit).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def has_conflict(
        self,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_session_id: Optional[int] = None
    ) -> bool:
        """Check if there's a conflicting session."""
        query = self.db.query(SessionModel).filter(
            SessionModel.instructor_id == instructor_id,
            SessionModel.status.in_([
                SessionStatus.PENDING_CONFIRMATION.value,
                SessionStatus.CONFIRMED.value,
                SessionStatus.IN_PROGRESS.value
            ]),
            # Time overlap: start < other_end AND end > other_start
            SessionModel.start_at < end_at,
            SessionModel.end_at > start_at,
        )

        if exclude_session_id:
            query = query.filter(SessionModel.id != exclude_session_id)

        return query.count() > 0

    def count_by_instructor(
        self,
        instructor_id: int,
        status: Optional[SessionStatus] = None
    ) -> int:
        """Count sessions for an instructor."""
        query = self.db.query(SessionModel).filter(
            SessionModel.instructor_id == instructor_id
        )

        if status:
            query = query.filter(SessionModel.status == status.value)

        return query.count()

    def get_recurring_series(self, parent_session_id: int) -> List[Session]:
        """Get all sessions in a recurring series."""
        db_models = self.db.query(SessionModel).filter(
            or_(
                SessionModel.id == parent_session_id,
                SessionModel.parent_session_id == parent_session_id
            )
        ).order_by(SessionModel.start_at).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def delete(self, session_id: int) -> bool:
        """Delete a session."""
        result = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).delete()
        self.db.commit()
        return result > 0
