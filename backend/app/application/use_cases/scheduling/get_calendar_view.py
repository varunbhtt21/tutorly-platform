"""Use case for getting instructor calendar view."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict

from app.domains.scheduling.repositories import (
    IAvailabilityRepository,
    ISessionRepository,
    ITimeOffRepository,
    IBookingSlotRepository,
)
from app.domains.scheduling.entities import Availability


@dataclass
class GetCalendarViewInput:
    """Input data for getting calendar view."""
    instructor_id: int
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format


@dataclass
class CalendarSlot:
    """Represents a time slot in the calendar."""
    start_at: str  # ISO datetime string
    end_at: str    # ISO datetime string
    status: str    # 'available', 'booked', 'blocked'
    slot_id: Optional[int] = None  # Individual slot ID for one-time slots
    availability_id: Optional[int] = None
    session_id: Optional[int] = None
    time_off_id: Optional[int] = None


@dataclass
class CalendarDay:
    """Calendar data for a single day."""
    date: str  # YYYY-MM-DD format
    slots: List[CalendarSlot] = field(default_factory=list)


@dataclass
class CalendarViewOutput:
    """Output data for calendar view."""
    start_date: str
    end_date: str
    instructor_id: int
    days: List[CalendarDay] = field(default_factory=list)


class GetCalendarViewUseCase:
    """
    Use case for getting instructor calendar data.

    Merges availability, sessions, and time-off into a unified calendar view.
    For one-time availability, uses individual BookingSlots from the database.
    For recurring availability, generates slots dynamically.
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
            availability_repo: Availability repository
            session_repo: Session repository
            time_off_repo: Time off repository
            booking_slot_repo: Booking slot repository (for individual slots)
        """
        self.availability_repo = availability_repo
        self.session_repo = session_repo
        self.time_off_repo = time_off_repo
        self.booking_slot_repo = booking_slot_repo

    def execute(self, input_data: GetCalendarViewInput) -> CalendarViewOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data containing instructor_id and date range

        Returns:
            CalendarViewOutput with calendar days and slots
        """
        # Parse dates
        start_date = date.fromisoformat(input_data.start_date)
        end_date = date.fromisoformat(input_data.end_date)
        instructor_id = input_data.instructor_id

        # Get availabilities (only recurring ones for dynamic slot generation)
        availabilities = self.availability_repo.get_by_instructor_date_range(
            instructor_id, start_date, end_date
        )

        # Separate recurring and one-time availabilities
        recurring_availabilities = [a for a in availabilities if a.is_recurring]
        one_time_availability_ids = {a.id for a in availabilities if not a.is_recurring}

        # Get sessions
        sessions = self.session_repo.get_by_instructor_date_range(
            instructor_id, start_date, end_date
        )

        # Get time offs
        time_offs = self.time_off_repo.get_by_instructor_date_range(
            instructor_id, start_date, end_date
        )

        # Get individual booking slots from database (for one-time availability)
        booking_slots = []
        if self.booking_slot_repo:
            booking_slots = self.booking_slot_repo.get_by_instructor_date_range(
                instructor_id, start_date, end_date
            )

        # Build days dictionary
        days_dict: Dict[str, List[CalendarSlot]] = {}
        current_date = start_date
        while current_date <= end_date:
            days_dict[current_date.isoformat()] = []
            current_date += timedelta(days=1)

        # Add individual booking slots from database (one-time availability)
        for booking_slot in booking_slots:
            slot_date = booking_slot.start_at.date().isoformat()
            if slot_date in days_dict:
                days_dict[slot_date].append(CalendarSlot(
                    start_at=booking_slot.start_at.isoformat(),
                    end_at=booking_slot.end_at.isoformat(),
                    status=booking_slot.status.value,
                    slot_id=booking_slot.id,
                    availability_id=booking_slot.availability_rule_id,
                    session_id=booking_slot.session_id,
                    time_off_id=None,
                ))

        # Generate availability slots for recurring availabilities only
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            for avail in recurring_availabilities:
                if avail.is_valid_on(current_date):
                    # Generate slots for this day
                    slots = avail.generate_slots_for_date(current_date)
                    for slot in slots:
                        days_dict[date_str].append(CalendarSlot(
                            start_at=slot["start_datetime"],
                            end_at=slot["end_datetime"],
                            status="available",
                            slot_id=None,  # No individual slot ID for recurring
                            availability_id=avail.id,
                            session_id=None,
                            time_off_id=None,
                        ))
            current_date += timedelta(days=1)

        # Mark booked slots from sessions (for recurring availability slots)
        for session in sessions:
            session_date = session.start_at.date().isoformat()
            if session_date in days_dict:
                # Find and update matching slot or add as booked
                session_start = session.start_at.isoformat()
                session_end = session.end_at.isoformat()
                slot_found = False
                for slot in days_dict[session_date]:
                    if slot.start_at == session_start and slot.slot_id is None:
                        # Only update recurring slots (slot_id is None)
                        slot.status = "booked"
                        slot.session_id = session.id
                        slot_found = True
                        break
                if not slot_found:
                    days_dict[session_date].append(CalendarSlot(
                        start_at=session_start,
                        end_at=session_end,
                        status="booked",
                        slot_id=None,
                        session_id=session.id,
                        time_off_id=None,
                    ))

        # Mark blocked slots from time offs
        for time_off in time_offs:
            time_off_date = time_off.start_at.date().isoformat()
            if time_off_date in days_dict:
                # Block all slots that overlap with time off
                time_off_start = time_off.start_at
                time_off_end = time_off.end_at
                for slot in days_dict[time_off_date]:
                    slot_start = datetime.fromisoformat(slot.start_at)
                    slot_end = datetime.fromisoformat(slot.end_at)
                    # Check for overlap
                    if slot_start < time_off_end and slot_end > time_off_start:
                        slot.status = "blocked"
                        slot.time_off_id = time_off.id

        # Convert to CalendarDay list
        days: List[CalendarDay] = []
        for date_str in sorted(days_dict.keys()):
            # Sort slots by start time
            sorted_slots = sorted(days_dict[date_str], key=lambda s: s.start_at)
            days.append(CalendarDay(date=date_str, slots=sorted_slots))

        return CalendarViewOutput(
            start_date=input_data.start_date,
            end_date=input_data.end_date,
            instructor_id=instructor_id,
            days=days,
        )
