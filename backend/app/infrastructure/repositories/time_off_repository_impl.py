"""SQLAlchemy implementation of ITimeOffRepository."""

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.domains.scheduling.entities import TimeOff
from app.domains.scheduling.repositories import ITimeOffRepository
from app.infrastructure.persistence.sqlalchemy_models import TimeOff as TimeOffModel
from app.infrastructure.persistence.mappers import TimeOffMapper


class TimeOffRepositoryImpl(ITimeOffRepository):
    """SQLAlchemy implementation of time off repository."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = TimeOffMapper()

    def save(self, time_off: TimeOff) -> TimeOff:
        """Save time off (create or update)."""
        if time_off.id:
            # Update existing
            db_model = self.db.query(TimeOffModel).filter(
                TimeOffModel.id == time_off.id
            ).first()

            if db_model:
                self.mapper.update_orm(db_model, time_off)
                self.db.commit()
                self.db.refresh(db_model)
                return self.mapper.to_domain(db_model)

        # Create new
        db_model = self.mapper.to_orm(time_off)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self.mapper.to_domain(db_model)

    def get_by_id(self, time_off_id: int) -> Optional[TimeOff]:
        """Get time off by ID."""
        db_model = self.db.query(TimeOffModel).filter(
            TimeOffModel.id == time_off_id
        ).first()

        if db_model:
            return self.mapper.to_domain(db_model)
        return None

    def get_by_instructor(self, instructor_id: int) -> List[TimeOff]:
        """Get all time offs for an instructor."""
        db_models = self.db.query(TimeOffModel).filter(
            TimeOffModel.instructor_id == instructor_id
        ).order_by(TimeOffModel.start_at).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[TimeOff]:
        """Get time offs overlapping a date range."""
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        db_models = self.db.query(TimeOffModel).filter(
            TimeOffModel.instructor_id == instructor_id,
            or_(
                # Non-recurring: overlaps with date range
                and_(
                    TimeOffModel.is_recurring == False,
                    TimeOffModel.start_at <= end_dt,
                    TimeOffModel.end_at >= start_dt
                ),
                # Recurring: always included (will be filtered by day)
                TimeOffModel.is_recurring == True
            )
        ).order_by(TimeOffModel.start_at).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def get_active_on_date(
        self,
        instructor_id: int,
        target_date: date
    ) -> List[TimeOff]:
        """Get time offs active on a specific date."""
        day_of_week = target_date.weekday()
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())

        db_models = self.db.query(TimeOffModel).filter(
            TimeOffModel.instructor_id == instructor_id,
            or_(
                # Non-recurring: date falls within time off period
                and_(
                    TimeOffModel.is_recurring == False,
                    TimeOffModel.start_at <= end_dt,
                    TimeOffModel.end_at >= start_dt
                ),
                # Recurring: matches day of week
                and_(
                    TimeOffModel.is_recurring == True,
                    TimeOffModel.recurrence_day == day_of_week
                )
            )
        ).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def has_overlap(
        self,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if there's an overlapping time off."""
        query = self.db.query(TimeOffModel).filter(
            TimeOffModel.instructor_id == instructor_id,
            TimeOffModel.is_recurring == False,
            # Time overlap: start < other_end AND end > other_start
            TimeOffModel.start_at < end_at,
            TimeOffModel.end_at > start_at,
        )

        if exclude_id:
            query = query.filter(TimeOffModel.id != exclude_id)

        return query.count() > 0

    def delete(self, time_off_id: int) -> bool:
        """Delete a time off."""
        result = self.db.query(TimeOffModel).filter(
            TimeOffModel.id == time_off_id
        ).delete()
        self.db.commit()
        return result > 0
