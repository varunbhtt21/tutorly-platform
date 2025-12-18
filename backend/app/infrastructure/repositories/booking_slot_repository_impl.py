"""SQLAlchemy implementation of IBookingSlotRepository."""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.domains.scheduling.entities import BookingSlot
from app.domains.scheduling.repositories import IBookingSlotRepository
from app.infrastructure.persistence.sqlalchemy_models import BookingSlot as BookingSlotModel
from app.infrastructure.persistence.mappers import BookingSlotMapper


class BookingSlotRepositoryImpl(IBookingSlotRepository):
    """SQLAlchemy implementation of booking slot repository."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.mapper = BookingSlotMapper()

    def save(self, slot: BookingSlot) -> BookingSlot:
        """Save a booking slot (create or update)."""
        if slot.id:
            # Update existing
            db_model = self.db.query(BookingSlotModel).filter(
                BookingSlotModel.id == slot.id
            ).first()

            if db_model:
                self.mapper.update_orm(db_model, slot)
                self.db.commit()
                self.db.refresh(db_model)
                return self.mapper.to_domain(db_model)

        # Create new
        db_model = self.mapper.to_orm(slot)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self.mapper.to_domain(db_model)

    def save_many(self, slots: List[BookingSlot]) -> List[BookingSlot]:
        """Save multiple booking slots at once."""
        result = []
        for slot in slots:
            db_model = self.mapper.to_orm(slot)
            self.db.add(db_model)

        self.db.commit()

        # Refresh all and return
        for db_model in self.db.new:
            self.db.refresh(db_model)

        # Re-query to get refreshed models
        # We need to fetch them again since db.new is cleared after commit
        return result

    def bulk_create(self, slots: List[BookingSlot]) -> List[BookingSlot]:
        """Bulk create booking slots efficiently."""
        db_models = [self.mapper.to_orm(slot) for slot in slots]
        self.db.add_all(db_models)
        self.db.commit()

        # Refresh all to get IDs
        for db_model in db_models:
            self.db.refresh(db_model)

        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_id(self, slot_id: int) -> Optional[BookingSlot]:
        """Get a booking slot by ID."""
        db_model = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.id == slot_id
        ).first()

        if db_model:
            return self.mapper.to_domain(db_model)
        return None

    def get_by_instructor(
        self,
        instructor_id: int,
        status: Optional[str] = None
    ) -> List[BookingSlot]:
        """Get all booking slots for an instructor."""
        query = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.instructor_id == instructor_id
        )

        if status:
            query = query.filter(BookingSlotModel.status == status)

        db_models = query.order_by(BookingSlotModel.start_at).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_instructor_date_range(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date,
        status: Optional[str] = None
    ) -> List[BookingSlot]:
        """Get booking slots for an instructor within a date range."""
        # Convert dates to datetime for comparison
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        query = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.instructor_id == instructor_id,
            BookingSlotModel.start_at >= start_dt,
            BookingSlotModel.start_at <= end_dt
        )

        if status:
            query = query.filter(BookingSlotModel.status == status)

        db_models = query.order_by(BookingSlotModel.start_at).all()
        return [self.mapper.to_domain(m) for m in db_models]

    def get_by_availability_rule(self, availability_rule_id: int) -> List[BookingSlot]:
        """Get all slots generated from a specific availability rule."""
        db_models = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.availability_rule_id == availability_rule_id
        ).order_by(BookingSlotModel.start_at).all()

        return [self.mapper.to_domain(m) for m in db_models]

    def delete(self, slot_id: int) -> bool:
        """Delete a booking slot."""
        result = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.id == slot_id
        ).delete()
        self.db.commit()
        return result > 0

    def delete_by_availability_rule(self, availability_rule_id: int) -> int:
        """Delete all slots generated from a specific availability rule."""
        result = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.availability_rule_id == availability_rule_id
        ).delete()
        self.db.commit()
        return result

    def delete_future_slots_by_rule(
        self,
        availability_rule_id: int,
        from_date: date
    ) -> int:
        """Delete future slots from a specific date for an availability rule."""
        from_dt = datetime.combine(from_date, datetime.min.time())

        result = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.availability_rule_id == availability_rule_id,
            BookingSlotModel.start_at >= from_dt,
            BookingSlotModel.status == "available"  # Only delete available slots
        ).delete()
        self.db.commit()
        return result

    def has_overlap(
        self,
        instructor_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if there's an overlapping slot."""
        query = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.instructor_id == instructor_id,
            # Time overlap: start < other_end AND end > other_start
            BookingSlotModel.start_at < end_at,
            BookingSlotModel.end_at > start_at,
        )

        if exclude_id:
            query = query.filter(BookingSlotModel.id != exclude_id)

        return query.count() > 0

    def get_available_slots_for_booking(
        self,
        instructor_id: int,
        start_date: date,
        end_date: date
    ) -> List[BookingSlot]:
        """Get only available slots for booking within a date range."""
        return self.get_by_instructor_date_range(
            instructor_id=instructor_id,
            start_date=start_date,
            end_date=end_date,
            status="available"
        )

    def get_by_instructor_and_time(
        self,
        instructor_id: int,
        start_at: datetime,
    ) -> Optional[BookingSlot]:
        """Get a booking slot by instructor and exact start time."""
        db_model = self.db.query(BookingSlotModel).filter(
            BookingSlotModel.instructor_id == instructor_id,
            BookingSlotModel.start_at == start_at,
        ).first()

        if db_model:
            return self.mapper.to_domain(db_model)
        return None
