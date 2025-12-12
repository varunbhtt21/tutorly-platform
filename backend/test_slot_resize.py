#!/usr/bin/env python
"""
Test script for slot resize functionality.

This script tests:
1. Creating one-time availability (should create booking_slots)
2. Viewing calendar to verify slot_id is returned
3. Resizing a slot (update start_at/end_at)
4. Verifying the slot was updated correctly
5. Verifying other slots are not affected
"""

import sys
from datetime import date, datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, '.')

from app.database.connection import SessionLocal
from app.infrastructure.repositories.availability_repository_impl import AvailabilityRepositoryImpl
from app.infrastructure.repositories.session_repository_impl import SessionRepositoryImpl
from app.infrastructure.repositories.time_off_repository_impl import TimeOffRepositoryImpl
from app.infrastructure.repositories.booking_slot_repository_impl import BookingSlotRepositoryImpl
from app.application.use_cases.scheduling.set_availability import SetAvailabilityUseCase, SetAvailabilityInput
from app.application.use_cases.scheduling.get_calendar_view import GetCalendarViewUseCase, GetCalendarViewInput
from app.application.use_cases.scheduling.update_slot import UpdateSlotUseCase, UpdateSlotInput
from app.application.use_cases.scheduling.delete_slot import DeleteSlotUseCase, DeleteSlotInput


def print_separator(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_slots(slots, title: str = "Slots"):
    print(f"\n{title}:")
    if not slots:
        print("  (none)")
        return
    for slot in slots:
        if hasattr(slot, 'id') and hasattr(slot, 'instructor_id'):
            # Domain entity (BookingSlot)
            print(f"  ID: {slot.id}, Start: {slot.start_at}, End: {slot.end_at}, Status: {slot.status}")
        elif hasattr(slot, 'slot_id'):
            # Dataclass from use case (CalendarSlot)
            print(f"  slot_id: {slot.slot_id}, Start: {slot.start_at}, End: {slot.end_at}, Status: {slot.status}, avail_id: {slot.availability_id}")
        else:
            print(f"  {slot}")


def test_slot_resize():
    """Main test function."""
    db = SessionLocal()

    try:
        # Initialize repositories
        availability_repo = AvailabilityRepositoryImpl(db)
        session_repo = SessionRepositoryImpl(db)
        time_off_repo = TimeOffRepositoryImpl(db)
        booking_slot_repo = BookingSlotRepositoryImpl(db)

        # Initialize use cases
        set_availability_uc = SetAvailabilityUseCase(availability_repo, booking_slot_repo)
        get_calendar_view_uc = GetCalendarViewUseCase(availability_repo, session_repo, time_off_repo, booking_slot_repo)
        update_slot_uc = UpdateSlotUseCase(booking_slot_repo)
        delete_slot_uc = DeleteSlotUseCase(booking_slot_repo)

        instructor_id = 21  # Test instructor
        test_date = (date.today() + timedelta(days=1)).isoformat()  # Tomorrow

        print_separator("TEST: Slot Resize Functionality")
        print(f"Instructor ID: {instructor_id}")
        print(f"Test Date: {test_date}")

        # ===================================================================
        # Step 1: Check existing booking slots
        # ===================================================================
        print_separator("Step 1: Check Existing Booking Slots")

        existing_slots = booking_slot_repo.get_by_instructor(instructor_id)
        print_slots(existing_slots, "Existing booking_slots in DB")

        # ===================================================================
        # Step 2: Create a new one-time availability for testing
        # ===================================================================
        print_separator("Step 2: Create One-Time Availability")

        # Create availability from 10:00 to 13:00 (3 hours = multiple slots)
        input_data = SetAvailabilityInput(
            instructor_id=instructor_id,
            availability_type="one_time",
            day_of_week=None,
            specific_date=test_date,
            start_time="10:00",
            end_time="13:00",
            slot_duration_minutes=50,
            break_minutes=10,
            timezone="UTC",
        )

        result = set_availability_uc.execute(input_data)
        print(f"Created availability ID: {result.id}")
        print(f"Slots created: {result.slots_created}")

        # ===================================================================
        # Step 3: Verify booking slots were created
        # ===================================================================
        print_separator("Step 3: Verify Booking Slots Created")

        new_slots = booking_slot_repo.get_by_instructor(instructor_id)
        print_slots(new_slots, "All booking_slots after creation")

        # Filter to only slots for today's test availability
        test_slots = [s for s in new_slots if s.availability_rule_id == result.id]
        print_slots(test_slots, f"Slots for availability {result.id}")

        if not test_slots:
            print("\nERROR: No booking slots were created!")
            return False

        # ===================================================================
        # Step 4: Get Calendar View and verify slot_id is returned
        # ===================================================================
        print_separator("Step 4: Get Calendar View")

        calendar_input = GetCalendarViewInput(
            instructor_id=instructor_id,
            start_date=test_date,
            end_date=test_date,
        )

        calendar_output = get_calendar_view_uc.execute(calendar_input)

        for day in calendar_output.days:
            if day.date == test_date:
                print_slots(day.slots, f"Calendar slots for {test_date}")

                # Check that slot_id is populated
                slots_with_id = [s for s in day.slots if s.slot_id is not None]
                slots_without_id = [s for s in day.slots if s.slot_id is None]

                print(f"\nSlots with slot_id: {len(slots_with_id)}")
                print(f"Slots without slot_id: {len(slots_without_id)}")

                if not slots_with_id:
                    print("\nERROR: Calendar view does not include slot_id!")
                    return False

        # ===================================================================
        # Step 5: Resize a slot
        # ===================================================================
        print_separator("Step 5: Resize a Slot")

        # Pick the first slot to resize
        slot_to_resize = test_slots[0]
        original_start = slot_to_resize.start_at
        original_end = slot_to_resize.end_at

        # Calculate new times (extend end by 5 minutes - within the break period)
        # Original slot is 10:00-10:50, next slot is 11:00-11:50
        # So we can extend to 10:55 (still within the 10 minute break)
        new_end = original_end + timedelta(minutes=5)

        print(f"Slot ID to resize: {slot_to_resize.id}")
        print(f"Original: {original_start} - {original_end}")
        print(f"New end time: {new_end}")

        # Perform the update
        update_input = UpdateSlotInput(
            slot_id=slot_to_resize.id,
            instructor_id=instructor_id,
            start_at=original_start.isoformat(),
            end_at=new_end.isoformat(),
        )

        update_result = update_slot_uc.execute(update_input)
        print(f"\nUpdate result:")
        print(f"  ID: {update_result.id}")
        print(f"  Start: {update_result.start_at}")
        print(f"  End: {update_result.end_at}")
        print(f"  Duration: {update_result.duration_minutes} minutes")

        # ===================================================================
        # Step 6: Verify the update and other slots
        # ===================================================================
        print_separator("Step 6: Verify Update and Other Slots")

        # Re-fetch all slots
        updated_slots = booking_slot_repo.get_by_instructor(instructor_id)
        print_slots(updated_slots, "All booking_slots after resize")

        # Check the resized slot
        resized_slot = booking_slot_repo.get_by_id(slot_to_resize.id)
        if resized_slot:
            print(f"\nResized slot {slot_to_resize.id}:")
            print(f"  Start: {resized_slot.start_at} (was: {original_start})")
            print(f"  End: {resized_slot.end_at} (was: {original_end})")

            if resized_slot.end_at == new_end:
                print("  ✓ End time updated correctly!")
            else:
                print("  ✗ End time NOT updated correctly!")
                return False
        else:
            print(f"\nERROR: Slot {slot_to_resize.id} not found after update!")
            return False

        # Check that other slots still exist
        remaining_test_slots = [s for s in updated_slots if s.availability_rule_id == result.id]
        print(f"\nRemaining slots for availability {result.id}: {len(remaining_test_slots)}")

        if len(remaining_test_slots) != len(test_slots):
            print(f"  ✗ ERROR: Expected {len(test_slots)} slots, found {len(remaining_test_slots)}")
            return False
        else:
            print(f"  ✓ All {len(test_slots)} slots still exist!")

        # ===================================================================
        # Step 7: Get Calendar View after resize
        # ===================================================================
        print_separator("Step 7: Calendar View After Resize")

        calendar_output_after = get_calendar_view_uc.execute(calendar_input)

        for day in calendar_output_after.days:
            if day.date == test_date:
                print_slots(day.slots, f"Calendar slots for {test_date} after resize")

        # ===================================================================
        # Step 8: Cleanup - Delete test availability and slots
        # ===================================================================
        print_separator("Step 8: Cleanup")

        # Delete the test slots
        for slot in remaining_test_slots:
            delete_input = DeleteSlotInput(
                slot_id=slot.id,
                instructor_id=instructor_id,
            )
            delete_slot_uc.execute(delete_input)
            print(f"Deleted slot {slot.id}")

        # Delete the availability
        availability_repo.delete(result.id)
        print(f"Deleted availability {result.id}")

        # Verify cleanup
        final_slots = booking_slot_repo.get_by_instructor(instructor_id)
        final_test_slots = [s for s in final_slots if s.availability_rule_id == result.id]
        print(f"\nRemaining test slots: {len(final_test_slots)}")

        print_separator("TEST COMPLETED SUCCESSFULLY")
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_slot_resize()
    sys.exit(0 if success else 1)
