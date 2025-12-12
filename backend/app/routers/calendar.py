"""
Calendar Router - Scheduling and Availability Management.

HTTP endpoints for instructor availability, time off, and calendar views using DDD principles:
- Thin controllers: Only handle HTTP concerns
- Delegate business logic to use cases
- Use domain entities and value objects
- Proper error handling and HTTP status codes
"""

from typing import List, Optional
from datetime import date, time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.domains.user.entities import User
from app.domains.scheduling.value_objects import DayOfWeek, AvailabilityType
from app.core.dependencies import (
    get_current_instructor,
    get_current_instructor_allow_inactive,
    get_set_availability_use_case,
    get_get_calendar_view_use_case,
    get_delete_availability_use_case,
    get_update_availability_use_case,
    get_add_time_off_use_case,
    get_delete_time_off_use_case,
    get_update_slot_use_case,
    get_delete_slot_use_case,
    get_availability_repository,
    get_time_off_repository,
    get_booking_slot_repository,
)
from app.application.use_cases.scheduling import (
    SetAvailabilityUseCase,
    GetCalendarViewUseCase,
    DeleteAvailabilityUseCase,
    UpdateAvailabilityUseCase,
    AddTimeOffUseCase,
    DeleteTimeOffUseCase,
    UpdateSlotUseCase,
    DeleteSlotUseCase,
)
from app.domains.scheduling.repositories import IAvailabilityRepository, ITimeOffRepository, IBookingSlotRepository


# ============================================================================
# Request/Response DTOs
# ============================================================================


# Availability DTOs

class SetRecurringAvailabilityRequest(BaseModel):
    """Request to set recurring weekly availability."""
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    slot_duration_minutes: int = Field(default=50, ge=15, le=120)
    break_minutes: int = Field(default=10, ge=0, le=60)


class SetOneTimeAvailabilityRequest(BaseModel):
    """Request to set one-time availability for a specific date."""
    specific_date: str = Field(..., description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    slot_duration_minutes: int = Field(default=50, ge=15, le=120)
    break_minutes: int = Field(default=10, ge=0, le=60)


class UpdateAvailabilityRequest(BaseModel):
    """Request to update an existing availability."""
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    slot_duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    break_minutes: Optional[int] = Field(None, ge=0, le=60)


class AvailabilityResponse(BaseModel):
    """Response for availability operations."""
    id: int
    instructor_id: int
    availability_type: str
    day_of_week: Optional[int]
    specific_date: Optional[str]
    start_time: str
    end_time: str
    slot_duration_minutes: int
    break_minutes: int


class AvailabilityListResponse(BaseModel):
    """Response for listing availability."""
    availabilities: List[AvailabilityResponse]
    total: int


# Time Off DTOs

class AddTimeOffRequest(BaseModel):
    """Request to add time off."""
    start_at: str = Field(..., description="Start datetime in ISO format")
    end_at: str = Field(..., description="End datetime in ISO format")
    reason: Optional[str] = Field(None, max_length=500)


class TimeOffResponse(BaseModel):
    """Response for time off operations."""
    id: int
    instructor_id: int
    start_at: str
    end_at: str
    reason: Optional[str]
    duration_hours: float


class TimeOffListResponse(BaseModel):
    """Response for listing time off."""
    time_offs: List[TimeOffResponse]
    total: int


# Calendar View DTOs

class CalendarSlotResponse(BaseModel):
    """A single slot in the calendar view."""
    start_at: str
    end_at: str
    status: str  # available, booked, blocked
    slot_id: Optional[int] = None  # Individual slot ID (for one-time slots)
    availability_id: Optional[int] = None
    session_id: Optional[int] = None
    time_off_id: Optional[int] = None


# Slot DTOs

class UpdateSlotRequest(BaseModel):
    """Request to update (resize) an individual slot."""
    start_at: Optional[str] = Field(None, description="New start datetime in ISO format")
    end_at: Optional[str] = Field(None, description="New end datetime in ISO format")


class SlotResponse(BaseModel):
    """Response for slot operations."""
    id: int
    instructor_id: int
    start_at: str
    end_at: str
    duration_minutes: int
    status: str
    availability_rule_id: Optional[int]


class CalendarDayResponse(BaseModel):
    """Calendar data for a single day."""
    date: str
    slots: List[CalendarSlotResponse]


class CalendarViewResponse(BaseModel):
    """Complete calendar view for a date range."""
    start_date: str
    end_date: str
    instructor_id: int
    days: List[CalendarDayResponse]


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


# Create router
router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def handle_domain_exception(e: Exception) -> None:
    """Convert domain exceptions to HTTP exceptions."""
    error_message = str(e)

    if "not found" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": error_message},
        )
    elif "overlap" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": "OVERLAP", "message": error_message},
        )
    elif "not authorized" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "FORBIDDEN", "message": error_message},
        )
    elif "invalid" in error_message.lower() or "must be" in error_message.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "VALIDATION_ERROR", "message": error_message},
        )
    else:
        import traceback
        print(f"Unexpected error: {error_message}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": error_message},
        )


def parse_time(time_str: str) -> time:
    """Parse time string to time object."""
    parts = time_str.split(":")
    return time(hour=int(parts[0]), minute=int(parts[1]))


def parse_date(date_str: str) -> date:
    """Parse date string to date object."""
    parts = date_str.split("-")
    return date(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]))


# ============================================================================
# Availability Endpoints
# ============================================================================


@router.post(
    "/availability/recurring",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set Recurring Weekly Availability",
    description="Set recurring weekly availability for a specific day of the week.",
)
async def set_recurring_availability(
    request: SetRecurringAvailabilityRequest,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: SetAvailabilityUseCase = Depends(get_set_availability_use_case),
) -> AvailabilityResponse:
    """Set recurring weekly availability."""
    try:
        from app.application.use_cases.scheduling.set_availability import SetAvailabilityInput

        input_data = SetAvailabilityInput(
            instructor_id=current_user.id,
            availability_type="recurring",
            day_of_week=request.day_of_week,
            specific_date=None,
            start_time=request.start_time,
            end_time=request.end_time,
            slot_duration_minutes=request.slot_duration_minutes,
            break_minutes=request.break_minutes,
        )

        output = use_case.execute(input_data)

        return AvailabilityResponse(
            id=output.id,
            instructor_id=output.instructor_id,
            availability_type=output.availability_type,
            day_of_week=output.day_of_week,
            specific_date=output.specific_date,
            start_time=output.start_time,
            end_time=output.end_time,
            slot_duration_minutes=output.slot_duration_minutes,
            break_minutes=output.break_minutes,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.post(
    "/availability/one-time",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set One-Time Availability",
    description="Set availability for a specific date.",
)
async def set_one_time_availability(
    request: SetOneTimeAvailabilityRequest,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: SetAvailabilityUseCase = Depends(get_set_availability_use_case),
) -> AvailabilityResponse:
    """Set one-time availability for a specific date."""
    try:
        from app.application.use_cases.scheduling.set_availability import SetAvailabilityInput

        input_data = SetAvailabilityInput(
            instructor_id=current_user.id,
            availability_type="one_time",
            day_of_week=None,
            specific_date=request.specific_date,
            start_time=request.start_time,
            end_time=request.end_time,
            slot_duration_minutes=request.slot_duration_minutes,
            break_minutes=request.break_minutes,
        )

        output = use_case.execute(input_data)

        return AvailabilityResponse(
            id=output.id,
            instructor_id=output.instructor_id,
            availability_type=output.availability_type,
            day_of_week=output.day_of_week,
            specific_date=output.specific_date,
            start_time=output.start_time,
            end_time=output.end_time,
            slot_duration_minutes=output.slot_duration_minutes,
            break_minutes=output.break_minutes,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "/availability",
    response_model=AvailabilityListResponse,
    summary="Get My Availability",
    description="Get all availability slots for the current instructor.",
)
async def get_my_availability(
    current_user: User = Depends(get_current_instructor_allow_inactive),
    availability_repo: IAvailabilityRepository = Depends(get_availability_repository),
    booking_slot_repo: IBookingSlotRepository = Depends(get_booking_slot_repository),
) -> AvailabilityListResponse:
    """
    Get all availability for the current instructor.

    This includes:
    1. Availability rules from the availability_slots table
    2. Synthetic availability derived from active booking slots (for data consistency)
    """
    try:
        # Get availability rules
        availabilities = availability_repo.get_by_instructor(current_user.id)

        # Track which availability rule IDs we've seen
        seen_availability_ids = {avail.id for avail in availabilities}

        items = []
        for avail in availabilities:
            # For one-time availability, get the actual time range from booking slots
            actual_start_time = avail.start_time
            actual_end_time = avail.end_time

            if avail.availability_type.value == "one_time" and avail.id:
                # Get slots for this availability to show actual current time range
                slots = booking_slot_repo.get_by_availability_rule(avail.id)
                if slots:
                    # Find min start and max end from actual slots
                    min_start = min(s.start_at for s in slots)
                    max_end = max(s.end_at for s in slots)
                    actual_start_time = time(min_start.hour, min_start.minute)
                    actual_end_time = time(max_end.hour, max_end.minute)

            items.append(AvailabilityResponse(
                id=avail.id,
                instructor_id=avail.instructor_id,
                availability_type=avail.availability_type.value,
                day_of_week=avail.day_of_week.value if avail.day_of_week else None,
                specific_date=avail.specific_date.isoformat() if avail.specific_date else None,
                start_time=actual_start_time.strftime("%H:%M"),
                end_time=actual_end_time.strftime("%H:%M"),
                slot_duration_minutes=avail.slot_duration_minutes,
                break_minutes=avail.break_minutes,
            ))

        # Also check for orphaned booking slots (slots without a valid availability rule)
        # These can happen if availability rules were deleted but slots remain
        all_slots = booking_slot_repo.get_by_instructor(current_user.id, status="available")

        # Group orphaned slots by date to create synthetic availability entries
        orphaned_slots_by_date = {}
        for slot in all_slots:
            rule_id = slot.availability_rule_id
            # Check if this slot's availability rule is not in our seen list
            if rule_id is None or rule_id not in seen_availability_ids:
                slot_date = slot.start_at.date().isoformat()
                if slot_date not in orphaned_slots_by_date:
                    orphaned_slots_by_date[slot_date] = []
                orphaned_slots_by_date[slot_date].append(slot)

        # Create synthetic availability entries for orphaned slots
        for date_str, slots in orphaned_slots_by_date.items():
            min_start = min(s.start_at for s in slots)
            max_end = max(s.end_at for s in slots)

            # Use negative ID to indicate synthetic entry (not a real availability rule)
            # Use the first slot's ID as a reference
            synthetic_id = -slots[0].id if slots[0].id else -1

            items.append(AvailabilityResponse(
                id=synthetic_id,
                instructor_id=current_user.id,
                availability_type="one_time",
                day_of_week=None,
                specific_date=date_str,
                start_time=time(min_start.hour, min_start.minute).strftime("%H:%M"),
                end_time=time(max_end.hour, max_end.minute).strftime("%H:%M"),
                slot_duration_minutes=slots[0].duration_minutes,
                break_minutes=0,  # Unknown for orphaned slots
            ))

        return AvailabilityListResponse(
            availabilities=items,
            total=len(items),
        )

    except Exception as e:
        handle_domain_exception(e)


@router.delete(
    "/availability/{availability_id}",
    response_model=MessageResponse,
    summary="Delete Availability",
    description="Delete an availability slot.",
)
async def delete_availability(
    availability_id: int,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: DeleteAvailabilityUseCase = Depends(get_delete_availability_use_case),
) -> MessageResponse:
    """Delete an availability slot."""
    try:
        deleted = use_case.execute(
            availability_id=availability_id,
            instructor_id=current_user.id,
        )

        if deleted:
            return MessageResponse(
                message="Availability deleted successfully",
                success=True,
            )
        else:
            return MessageResponse(
                message="Availability not found",
                success=False,
            )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.put(
    "/availability/{availability_id}",
    response_model=MessageResponse,
    summary="Update Availability",
    description="Update an existing availability slot's time window.",
)
async def update_availability(
    availability_id: int,
    request: UpdateAvailabilityRequest,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: UpdateAvailabilityUseCase = Depends(get_update_availability_use_case),
) -> MessageResponse:
    """Update an availability slot's time window."""
    try:
        from app.application.use_cases.scheduling.update_availability import UpdateAvailabilityInput

        input_data = UpdateAvailabilityInput(
            availability_id=availability_id,
            instructor_id=current_user.id,
            start_time=request.start_time,
            end_time=request.end_time,
            slot_duration_minutes=request.slot_duration_minutes,
            break_minutes=request.break_minutes,
        )

        output = use_case.execute(input_data)

        return MessageResponse(
            message=output.message,
            success=output.success,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# Time Off Endpoints
# ============================================================================


@router.post(
    "/time-off",
    response_model=TimeOffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Time Off",
    description="Add a time off period when the instructor is unavailable.",
)
async def add_time_off(
    request: AddTimeOffRequest,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: AddTimeOffUseCase = Depends(get_add_time_off_use_case),
) -> TimeOffResponse:
    """Add a time off period."""
    try:
        from app.application.use_cases.scheduling.add_time_off import AddTimeOffInput

        input_data = AddTimeOffInput(
            instructor_id=current_user.id,
            start_at=request.start_at,
            end_at=request.end_at,
            reason=request.reason,
        )

        output = use_case.execute(input_data)

        return TimeOffResponse(
            id=output.id,
            instructor_id=output.instructor_id,
            start_at=output.start_at,
            end_at=output.end_at,
            reason=output.reason,
            duration_hours=output.duration_hours,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "/time-off",
    response_model=TimeOffListResponse,
    summary="Get My Time Off",
    description="Get all time off periods for the current instructor.",
)
async def get_my_time_off(
    current_user: User = Depends(get_current_instructor_allow_inactive),
    time_off_repo: ITimeOffRepository = Depends(get_time_off_repository),
) -> TimeOffListResponse:
    """Get all time off for the current instructor."""
    try:
        time_offs = time_off_repo.get_by_instructor(current_user.id)

        items = []
        for to in time_offs:
            items.append(TimeOffResponse(
                id=to.id,
                instructor_id=to.instructor_id,
                start_at=to.start_at.isoformat(),
                end_at=to.end_at.isoformat(),
                reason=to.reason,
                duration_hours=to.duration_hours,
            ))

        return TimeOffListResponse(
            time_offs=items,
            total=len(items),
        )

    except Exception as e:
        handle_domain_exception(e)


@router.delete(
    "/time-off/{time_off_id}",
    response_model=MessageResponse,
    summary="Delete Time Off",
    description="Delete a time off period.",
)
async def delete_time_off(
    time_off_id: int,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: DeleteTimeOffUseCase = Depends(get_delete_time_off_use_case),
) -> MessageResponse:
    """Delete a time off period."""
    try:
        from app.application.use_cases.scheduling.delete_time_off import DeleteTimeOffInput

        input_data = DeleteTimeOffInput(
            time_off_id=time_off_id,
            instructor_id=current_user.id,
        )

        output = use_case.execute(input_data)

        return MessageResponse(
            message=output.message,
            success=output.success,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# Calendar View Endpoints
# ============================================================================


@router.get(
    "/view",
    response_model=CalendarViewResponse,
    summary="Get Calendar View",
    description="Get calendar view for a date range showing availability, sessions, and time off.",
)
async def get_calendar_view(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: GetCalendarViewUseCase = Depends(get_get_calendar_view_use_case),
) -> CalendarViewResponse:
    """Get calendar view for date range."""
    try:
        from app.application.use_cases.scheduling.get_calendar_view import GetCalendarViewInput

        input_data = GetCalendarViewInput(
            instructor_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )

        output = use_case.execute(input_data)

        # Convert to response format
        days = []
        for day in output.days:
            slots = []
            for slot in day.slots:
                slots.append(CalendarSlotResponse(
                    start_at=slot.start_at,
                    end_at=slot.end_at,
                    status=slot.status,
                    slot_id=slot.slot_id,
                    availability_id=slot.availability_id,
                    session_id=slot.session_id,
                    time_off_id=slot.time_off_id,
                ))
            days.append(CalendarDayResponse(
                date=day.date,
                slots=slots,
            ))

        return CalendarViewResponse(
            start_date=output.start_date,
            end_date=output.end_date,
            instructor_id=output.instructor_id,
            days=days,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.get(
    "/view/public/{instructor_id}",
    response_model=CalendarViewResponse,
    summary="Get Public Calendar View",
    description="Get public calendar view for an instructor (for students to see available slots).",
)
async def get_public_calendar_view(
    instructor_id: int,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    use_case: GetCalendarViewUseCase = Depends(get_get_calendar_view_use_case),
) -> CalendarViewResponse:
    """Get public calendar view for an instructor."""
    try:
        from app.application.use_cases.scheduling.get_calendar_view import GetCalendarViewInput

        input_data = GetCalendarViewInput(
            instructor_id=instructor_id,
            start_date=start_date,
            end_date=end_date,
        )

        output = use_case.execute(input_data)

        # Convert to response format - only show available slots for public view
        days = []
        for day in output.days:
            slots = []
            for slot in day.slots:
                # For public view, only show available slots
                if slot.status == "available":
                    slots.append(CalendarSlotResponse(
                        start_at=slot.start_at,
                        end_at=slot.end_at,
                        status=slot.status,
                        slot_id=slot.slot_id,
                        session_id=None,
                        time_off_id=None,
                    ))
            days.append(CalendarDayResponse(
                date=day.date,
                slots=slots,
            ))

        return CalendarViewResponse(
            start_date=output.start_date,
            end_date=output.end_date,
            instructor_id=output.instructor_id,
            days=days,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


# ============================================================================
# Individual Slot Endpoints (for one-time availability)
# ============================================================================


@router.put(
    "/slots/{slot_id}",
    response_model=SlotResponse,
    summary="Update Individual Slot",
    description="Update (resize) an individual booking slot. Only works for one-time availability slots.",
)
async def update_slot(
    slot_id: int,
    request: UpdateSlotRequest,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: UpdateSlotUseCase = Depends(get_update_slot_use_case),
) -> SlotResponse:
    """Update (resize) an individual slot."""
    try:
        from app.application.use_cases.scheduling.update_slot import UpdateSlotInput

        input_data = UpdateSlotInput(
            slot_id=slot_id,
            instructor_id=current_user.id,
            start_at=request.start_at,
            end_at=request.end_at,
        )

        output = use_case.execute(input_data)

        return SlotResponse(
            id=output.id,
            instructor_id=output.instructor_id,
            start_at=output.start_at,
            end_at=output.end_at,
            duration_minutes=output.duration_minutes,
            status=output.status,
            availability_rule_id=output.availability_rule_id,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)


@router.delete(
    "/slots/{slot_id}",
    response_model=MessageResponse,
    summary="Delete Individual Slot",
    description="Delete an individual booking slot. Only works for one-time availability slots that are not booked.",
)
async def delete_slot(
    slot_id: int,
    current_user: User = Depends(get_current_instructor_allow_inactive),
    use_case: DeleteSlotUseCase = Depends(get_delete_slot_use_case),
) -> MessageResponse:
    """Delete an individual slot."""
    try:
        from app.application.use_cases.scheduling.delete_slot import DeleteSlotInput

        input_data = DeleteSlotInput(
            slot_id=slot_id,
            instructor_id=current_user.id,
        )

        output = use_case.execute(input_data)

        return MessageResponse(
            message=output.message,
            success=output.success,
        )

    except ValueError as e:
        handle_domain_exception(e)
    except Exception as e:
        handle_domain_exception(e)
