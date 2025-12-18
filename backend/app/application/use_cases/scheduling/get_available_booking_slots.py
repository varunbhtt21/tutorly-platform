"""Use case for getting available booking slots for student booking flow."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional, Set

from app.domains.scheduling.repositories import (
    IAvailabilityRepository,
    ISessionRepository,
    ITimeOffRepository,
    IBookingSlotRepository,
)
from app.domains.scheduling.entities import BookingSlot


@dataclass
class GetAvailableBookingSlotsInput:
    """Input data for getting available booking slots."""
    instructor_id: int
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format


@dataclass
class BookingSlotOutput:
    """Represents a single available booking slot."""
    id: Optional[int]  # None for dynamically generated recurring slots
    instructor_id: int
    start_at: str  # ISO datetime string
    end_at: str    # ISO datetime string
    duration_minutes: int
    status: str = "available"
    availability_rule_id: Optional[int] = None
    is_recurring: bool = False  # True if generated from recurring rule


@dataclass
class GetAvailableBookingSlotsOutput:
    """Output data for available booking slots."""
    instructor_id: int
    start_date: str
    end_date: str
    slots: List[BookingSlotOutput] = field(default_factory=list)
    total: int = 0


class GetAvailableBookingSlotsUseCase:
    """
    Use case for getting available booking slots for student booking flow.

    This use case combines:
    1. One-time availability slots from the booking_slots table
    2. Dynamically generated slots from recurring availability rules

    It also filters out:
    - Slots that overlap with booked sessions
    - Slots that overlap with time-off periods
    - Slots in the past

    This provides a unified view of all available slots for booking,
    regardless of whether they come from one-time or recurring availability.
    """

    def __init__(
        self,
        availability_repo: IAvailabilityRepository,
        session_repo: ISessionRepository,
        time_off_repo: ITimeOffRepository,
        booking_slot_repo: Optional[IBookingSlotRepository] = None,
    ):
        """
        Initialize use case with repositories.

        Args:
            availability_repo: Availability repository for rules
            session_repo: Session repository for booked sessions
            time_off_repo: Time off repository for blocked periods
            booking_slot_repo: Booking slot repository for one-time slots
        """
        self.availability_repo = availability_repo
        self.session_repo = session_repo
        self.time_off_repo = time_off_repo
        self.booking_slot_repo = booking_slot_repo

    def execute(self, input_data: GetAvailableBookingSlotsInput) -> GetAvailableBookingSlotsOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data containing instructor_id and date range

        Returns:
            GetAvailableBookingSlotsOutput with available booking slots
        """
        # Parse dates
        start_date = date.fromisoformat(input_data.start_date)
        end_date = date.fromisoformat(input_data.end_date)
        instructor_id = input_data.instructor_id
        now = datetime.utcnow()

        # Collect all available slots
        available_slots: List[BookingSlotOutput] = []

        # Track times that are already occupied to avoid duplicates
        occupied_times: Set[str] = set()

        # 1. Get booked session times to filter them out
        sessions = self.session_repo.get_by_instructor_date_range(
            instructor_id, start_date, end_date
        )
        booked_times: Set[str] = set()
        for session in sessions:
            booked_times.add(session.start_at.isoformat())

        # 2. Get time-off periods
        time_offs = self.time_off_repo.get_by_instructor_date_range(
            instructor_id, start_date, end_date
        )

        # 3. Get one-time slots from booking_slots table
        if self.booking_slot_repo:
            booking_slots = self.booking_slot_repo.get_available_slots_for_booking(
                instructor_id=instructor_id,
                start_date=start_date,
                end_date=end_date
            )

            for slot in booking_slots:
                slot_start_str = slot.start_at.isoformat()

                # Skip if in the past
                if slot.start_at <= now:
                    continue

                # Skip if already booked
                if slot_start_str in booked_times:
                    continue

                # Skip if blocked by time-off
                if self._is_blocked_by_time_off(slot.start_at, slot.end_at, time_offs):
                    continue

                # Mark as occupied
                occupied_times.add(slot_start_str)

                available_slots.append(BookingSlotOutput(
                    id=slot.id,
                    instructor_id=slot.instructor_id,
                    start_at=slot_start_str,
                    end_at=slot.end_at.isoformat(),
                    duration_minutes=slot.duration_minutes,
                    status="available",
                    availability_rule_id=slot.availability_rule_id,
                    is_recurring=False,
                ))

        # 4. Get recurring availability rules and generate slots
        availabilities = self.availability_repo.get_by_instructor_date_range(
            instructor_id, start_date, end_date
        )
        recurring_availabilities = [a for a in availabilities if a.is_recurring]

        # Generate slots for each day in the range
        current_date = start_date
        while current_date <= end_date:
            for avail in recurring_availabilities:
                if avail.is_valid_on(current_date):
                    # Generate slots for this day
                    slots_data = avail.generate_slots_for_date(current_date)
                    for slot_data in slots_data:
                        slot_start_str = slot_data["start_datetime"]
                        slot_end_str = slot_data["end_datetime"]
                        slot_start = datetime.fromisoformat(slot_start_str)
                        slot_end = datetime.fromisoformat(slot_end_str)

                        # Skip if in the past
                        if slot_start <= now:
                            continue

                        # Skip if this time slot is already occupied (by one-time slot)
                        if slot_start_str in occupied_times:
                            continue

                        # Skip if already booked
                        if slot_start_str in booked_times:
                            continue

                        # Skip if blocked by time-off
                        if self._is_blocked_by_time_off(slot_start, slot_end, time_offs):
                            continue

                        # Mark as occupied
                        occupied_times.add(slot_start_str)

                        available_slots.append(BookingSlotOutput(
                            id=None,  # No ID for dynamically generated slots
                            instructor_id=instructor_id,
                            start_at=slot_start_str,
                            end_at=slot_end_str,
                            duration_minutes=slot_data["duration_minutes"],
                            status="available",
                            availability_rule_id=avail.id,
                            is_recurring=True,
                        ))

            current_date += timedelta(days=1)

        # Sort slots by start time
        available_slots.sort(key=lambda s: s.start_at)

        return GetAvailableBookingSlotsOutput(
            instructor_id=instructor_id,
            start_date=input_data.start_date,
            end_date=input_data.end_date,
            slots=available_slots,
            total=len(available_slots),
        )

    def _is_blocked_by_time_off(
        self,
        slot_start: datetime,
        slot_end: datetime,
        time_offs: list
    ) -> bool:
        """Check if a slot overlaps with any time-off period."""
        for time_off in time_offs:
            # Check for overlap: start < other_end AND end > other_start
            if slot_start < time_off.end_at and slot_end > time_off.start_at:
                return True
        return False
