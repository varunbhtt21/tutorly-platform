"""Use case for setting instructor availability."""

from dataclasses import dataclass
from datetime import date, time, datetime, timedelta
from typing import Optional, List

from app.domains.scheduling.entities import Availability, BookingSlot
from app.domains.scheduling.repositories import IAvailabilityRepository, IBookingSlotRepository
from app.domains.scheduling.value_objects import AvailabilityType, DayOfWeek


@dataclass
class SetAvailabilityInput:
    """Input data for setting availability."""
    instructor_id: int
    availability_type: str  # 'recurring' or 'one_time'
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    day_of_week: Optional[int] = None  # 0-6 for recurring
    specific_date: Optional[str] = None  # YYYY-MM-DD for one-time
    slot_duration_minutes: int = 50
    break_minutes: int = 10
    timezone: str = "UTC"
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None


@dataclass
class SetAvailabilityOutput:
    """Output data from setting availability."""
    id: int
    instructor_id: int
    availability_type: str
    day_of_week: Optional[int]
    specific_date: Optional[str]
    start_time: str
    end_time: str
    slot_duration_minutes: int
    break_minutes: int
    timezone: str
    is_active: bool
    slots_created: int = 0  # Number of individual slots created


class SetAvailabilityUseCase:
    """
    Use case for creating or updating instructor availability.

    Handles both recurring (weekly) and one-time availability slots.
    Also generates individual BookingSlots for one-time availability.
    """

    def __init__(
        self,
        availability_repo: IAvailabilityRepository,
        booking_slot_repo: Optional[IBookingSlotRepository] = None
    ):
        """
        Initialize use case with repositories.

        Args:
            availability_repo: Availability repository implementation
            booking_slot_repo: Booking slot repository (optional for backward compatibility)
        """
        self.availability_repo = availability_repo
        self.booking_slot_repo = booking_slot_repo

    def execute(self, input_data: SetAvailabilityInput) -> SetAvailabilityOutput:
        """
        Execute the use case.

        Args:
            input_data: Input data for setting availability

        Returns:
            SetAvailabilityOutput with created/updated availability

        Raises:
            ValueError: If input validation fails or overlap detected
        """
        # Parse time values
        start_time = time.fromisoformat(input_data.start_time)
        end_time = time.fromisoformat(input_data.end_time)

        # Parse dates
        valid_from = date.today()
        if input_data.valid_from:
            valid_from = date.fromisoformat(input_data.valid_from)

        valid_until = None
        if input_data.valid_until:
            valid_until = date.fromisoformat(input_data.valid_until)

        # Create domain entity based on type
        availability_type = AvailabilityType(input_data.availability_type)

        if availability_type == AvailabilityType.RECURRING:
            if input_data.day_of_week is None:
                raise ValueError("day_of_week is required for recurring availability")

            day_of_week = DayOfWeek.from_int(input_data.day_of_week)

            # Check for overlap
            if self.availability_repo.has_overlap(
                instructor_id=input_data.instructor_id,
                day_of_week=day_of_week,
                specific_date=None,
                start_time=start_time,
                end_time=end_time,
            ):
                raise ValueError(f"Overlapping availability exists for {day_of_week.name}")

            availability = Availability.create_recurring(
                instructor_id=input_data.instructor_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                timezone=input_data.timezone,
                slot_duration_minutes=input_data.slot_duration_minutes,
                break_minutes=input_data.break_minutes,
                valid_from=valid_from,
                valid_until=valid_until,
            )
        else:  # ONE_TIME
            if input_data.specific_date is None:
                raise ValueError("specific_date is required for one-time availability")

            specific_date = date.fromisoformat(input_data.specific_date)

            # Check for overlap
            if self.availability_repo.has_overlap(
                instructor_id=input_data.instructor_id,
                day_of_week=None,
                specific_date=specific_date,
                start_time=start_time,
                end_time=end_time,
            ):
                raise ValueError(f"Overlapping availability exists for {specific_date}")

            availability = Availability.create_one_time(
                instructor_id=input_data.instructor_id,
                specific_date=specific_date,
                start_time=start_time,
                end_time=end_time,
                timezone=input_data.timezone,
                slot_duration_minutes=input_data.slot_duration_minutes,
                break_minutes=input_data.break_minutes,
            )

        # Save to repository
        saved = self.availability_repo.save(availability)

        # Generate and save individual BookingSlots for one-time availability
        slots_created = 0
        if self.booking_slot_repo and availability_type == AvailabilityType.ONE_TIME:
            slots_created = self._generate_booking_slots(saved)

        return SetAvailabilityOutput(
            id=saved.id,
            instructor_id=saved.instructor_id,
            availability_type=saved.availability_type.value,
            day_of_week=saved.day_of_week.value if saved.day_of_week else None,
            specific_date=saved.specific_date.isoformat() if saved.specific_date else None,
            start_time=saved.start_time.isoformat(),
            end_time=saved.end_time.isoformat(),
            slot_duration_minutes=saved.slot_duration_minutes,
            break_minutes=saved.break_minutes,
            timezone=saved.timezone,
            is_active=saved.is_active,
            slots_created=slots_created,
        )

    def _generate_booking_slots(self, availability: Availability) -> int:
        """
        Generate individual BookingSlots from an availability rule.

        For one-time availability, generates slots for the specific date.
        Returns the number of slots created.
        """
        if not self.booking_slot_repo:
            return 0

        target_date = availability.specific_date
        if not target_date:
            return 0

        # Generate slot data from availability
        slot_data_list = availability.generate_slots_for_date(target_date)

        # Create BookingSlot entities
        booking_slots = []
        for slot_data in slot_data_list:
            start_dt = datetime.fromisoformat(slot_data["start_datetime"])
            end_dt = datetime.fromisoformat(slot_data["end_datetime"])

            booking_slot = BookingSlot.create(
                instructor_id=availability.instructor_id,
                availability_rule_id=availability.id,
                start_at=start_dt,
                end_at=end_dt,
                duration_minutes=slot_data["duration_minutes"],
                timezone=availability.timezone,
            )
            booking_slots.append(booking_slot)

        # Bulk save
        if booking_slots:
            self.booking_slot_repo.bulk_create(booking_slots)

        return len(booking_slots)
