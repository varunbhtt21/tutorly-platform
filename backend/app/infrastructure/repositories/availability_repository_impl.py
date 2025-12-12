"""SQLAlchemy implementation of IAvailabilityRepository."""

from datetime import date, time
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.domains.scheduling.entities import Availability
from app.domains.scheduling.repositories import IAvailabilityRepository
from app.domains.scheduling.value_objects import DayOfWeek
from app.infrastructure.persistence.sqlalchemy_models import AvailabilitySlot
from app.infrastructure.persistence.mappers import AvailabilityMapper


class AvailabilityRepositoryImpl(IAvailabilityRepository):
    """SQLAlchemy implementation of availability repository."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = AvailabilityMapper()

    def save(self, availability: Availability) -> Availability:
        """Save availability (create or update)."""
        if availability.id:
            # Update existing
            db_model = self.db.query(AvailabilitySlot).filter(
                AvailabilitySlot.id == availability.id
            ).first()

            if db_model:
                self.mapper.update_orm(db_model, availability)
                self.db.commit()
                self.db.refresh(db_model)
                return self.mapper.to_domain(db_model)

        # Create new
        db_model = self.mapper.to_orm(availability)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self.mapper.to_domain(db_model)

    def get_by_id(self, availability_id: int) -> Optional[Availability]:
        """Get availability by ID."""
        db_model = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == availability_id
        ).first()

        if db_model:
            return self.mapper.to_domain(db_model)
        return None

    def get_by_instructor(
        self,
        instructor_id: int,
        active_only: bool = True
    ) -> List[Availability]:
        """Get all availabilities for an instructor."""
        query = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.instructor_id == instructor_id
        )

        if active_only:
            query = query.filter(AvailabilitySlot.is_active == True)

        db_models = query.order_by(AvailabilitySlot.day_of_week, AvailabilitySlot.start_time).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_instructor_and_date(
        self,
        instructor_id: int,
        target_date: date
    ) -> List[Availability]:
        """Get availabilities valid for a specific date."""
        day_of_week = target_date.weekday()
        target_date_str = target_date.isoformat()

        # Get recurring availabilities for this day of week
        # OR one-time availabilities for this specific date
        query = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.instructor_id == instructor_id,
            AvailabilitySlot.is_active == True,
            or_(
                # Recurring: matches day of week and within validity period
                and_(
                    AvailabilitySlot.availability_type == "recurring",
                    AvailabilitySlot.day_of_week == day_of_week,
                    AvailabilitySlot.valid_from <= target_date_str,
                    or_(
                        AvailabilitySlot.valid_until.is_(None),
                        AvailabilitySlot.valid_until >= target_date_str
                    )
                ),
                # One-time: matches specific date
                and_(
                    AvailabilitySlot.availability_type == "one_time",
                    AvailabilitySlot.specific_date == target_date_str
                )
            )
        )

        db_models = query.order_by(AvailabilitySlot.start_time).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_instructor_and_day(
        self,
        instructor_id: int,
        day_of_week: DayOfWeek
    ) -> List[Availability]:
        """Get recurring availabilities for a specific day of week."""
        db_models = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.instructor_id == instructor_id,
            AvailabilitySlot.availability_type == "recurring",
            AvailabilitySlot.day_of_week == day_of_week.value,
            AvailabilitySlot.is_active == True
        ).order_by(AvailabilitySlot.start_time).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[Availability]:
        """Get all availabilities overlapping a date range."""
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()

        # Get all recurring that overlap the range + one-time within range
        query = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.instructor_id == instructor_id,
            AvailabilitySlot.is_active == True,
            or_(
                # Recurring: valid period overlaps with date range
                and_(
                    AvailabilitySlot.availability_type == "recurring",
                    AvailabilitySlot.valid_from <= end_str,
                    or_(
                        AvailabilitySlot.valid_until.is_(None),
                        AvailabilitySlot.valid_until >= start_str
                    )
                ),
                # One-time: specific date within range
                and_(
                    AvailabilitySlot.availability_type == "one_time",
                    AvailabilitySlot.specific_date >= start_str,
                    AvailabilitySlot.specific_date <= end_str
                )
            )
        )

        db_models = query.order_by(AvailabilitySlot.day_of_week, AvailabilitySlot.start_time).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def delete(self, availability_id: int) -> bool:
        """Delete an availability."""
        result = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == availability_id
        ).delete()
        self.db.commit()
        return result > 0

    def deactivate(self, availability_id: int) -> bool:
        """Deactivate an availability (soft delete)."""
        result = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == availability_id
        ).update({"is_active": False})
        self.db.commit()
        return result > 0

    def has_overlap(
        self,
        instructor_id: int,
        day_of_week: Optional[DayOfWeek],
        specific_date: Optional[date],
        start_time: time,
        end_time: time,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if there's an overlapping availability."""
        start_str = start_time.isoformat()
        end_str = end_time.isoformat()

        query = self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.instructor_id == instructor_id,
            AvailabilitySlot.is_active == True,
            # Time overlap: start < other_end AND end > other_start
            AvailabilitySlot.start_time < end_str,
            AvailabilitySlot.end_time > start_str,
        )

        if day_of_week is not None:
            query = query.filter(
                AvailabilitySlot.availability_type == "recurring",
                AvailabilitySlot.day_of_week == day_of_week.value
            )
        elif specific_date is not None:
            query = query.filter(
                AvailabilitySlot.availability_type == "one_time",
                AvailabilitySlot.specific_date == specific_date.isoformat()
            )

        if exclude_id:
            query = query.filter(AvailabilitySlot.id != exclude_id)

        return query.count() > 0
