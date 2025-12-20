"""
Test script for 100ms classroom integration.

This script creates a test room and generates meeting tokens to verify
that 100ms is properly configured and working.

Usage:
    cd backend
    python -m tests.test_100ms_classroom
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.dev")

from app.infrastructure.video_providers.hundredms_provider import HundredMsVideoProvider
from app.domains.classroom.services.video_provider import RoomConfig, ParticipantRole


def test_100ms():
    """Test 100ms room creation and token generation."""

    # Get credentials from environment
    access_key = os.getenv("HMS_ACCESS_KEY")
    app_secret = os.getenv("HMS_APP_SECRET")
    template_id = os.getenv("HMS_TEMPLATE_ID") or None

    if not access_key or not app_secret:
        print("Error: HMS_ACCESS_KEY and HMS_APP_SECRET must be set in .env.dev")
        print(f"   HMS_ACCESS_KEY: {'Set' if access_key else 'Not set'}")
        print(f"   HMS_APP_SECRET: {'Set' if app_secret else 'Not set'}")
        print()
        print("To get credentials:")
        print("1. Sign up at https://100ms.live")
        print("2. Create a new app")
        print("3. Go to Developer > Access Keys")
        print("4. Create a new access key")
        print("5. Copy Access Key and App Secret to .env.dev")
        return

    print("100ms credentials found")
    print(f"   Access Key: {access_key[:10]}...")
    print(f"   App Secret: {app_secret[:10]}...")
    if template_id:
        print(f"   Template ID: {template_id}")
    print()

    # Initialize provider
    provider = HundredMsVideoProvider(
        access_key=access_key,
        app_secret=app_secret,
        template_id=template_id,
    )

    # Create a test room
    test_session_id = 99999  # Dummy session ID for testing
    room_config = RoomConfig(
        session_id=test_session_id,
        instructor_id=1,
        student_id=2,
        scheduled_start=datetime.now(timezone.utc) + timedelta(minutes=5),
        duration_minutes=60,
    )

    print("Creating test room...")
    try:
        room_info = provider.create_room(room_config)
        print("Room created successfully!")
        print(f"   Room ID: {room_info.room_id}")
        print(f"   Room Name: {room_info.room_name}")
        print(f"   Provider: {room_info.provider}")
        print(f"   Created At: {room_info.created_at}")
        print()
    except Exception as e:
        print(f"Failed to create room: {e}")
        return

    # Generate meeting token for instructor
    print("Generating meeting token for instructor...")
    try:
        instructor_token = provider.create_meeting_token(
            room_name=room_info.room_name,
            participant_id=1,
            participant_name="Test Instructor",
            participant_role=ParticipantRole.INSTRUCTOR,
            expires_in_minutes=120,
        )
        print("Instructor token generated!")
        print(f"   Token (first 50 chars): {instructor_token.token[:50]}...")
        print(f"   Role: {instructor_token.participant_role.value}")
        print(f"   Expires At: {instructor_token.expires_at}")
        print()
    except Exception as e:
        print(f"Failed to generate instructor token: {e}")
        return

    # Generate meeting token for student
    print("Generating meeting token for student...")
    try:
        student_token = provider.create_meeting_token(
            room_name=room_info.room_name,
            participant_id=2,
            participant_name="Test Student",
            participant_role=ParticipantRole.STUDENT,
            expires_in_minutes=120,
        )
        print("Student token generated!")
        print(f"   Token (first 50 chars): {student_token.token[:50]}...")
        print(f"   Role: {student_token.participant_role.value}")
        print(f"   Expires At: {student_token.expires_at}")
        print()
    except Exception as e:
        print(f"Failed to generate student token: {e}")
        return

    # Print tokens for testing with 100ms dashboard
    print("=" * 60)
    print("TOKENS FOR TESTING")
    print("=" * 60)
    print()
    print("Use these tokens in the 100ms web app or SDK to test:")
    print()
    print("ROOM ID:")
    print(f"   {room_info.room_id}")
    print()
    print("INSTRUCTOR TOKEN:")
    print(f"   {instructor_token.token}")
    print()
    print("STUDENT TOKEN:")
    print(f"   {student_token.token}")
    print()
    print("=" * 60)
    print("TESTING INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. Go to https://dashboard.100ms.live")
    print("2. Navigate to your app's Rooms section")
    print("3. Find the room: tutorly-session-99999")
    print("4. Click 'Join Room' with the instructor token")
    print("5. Open another browser/incognito with student token")
    print("6. Both should connect to the same room")
    print()
    print("Or use the 100ms SDK in your frontend with these tokens.")
    print("=" * 60)

    # Cleanup option
    print()
    cleanup = input("Do you want to delete/disable the test room? (y/n): ").lower().strip()
    if cleanup == 'y':
        print("Disabling test room...")
        if provider.delete_room(room_info.room_name):
            print("Room disabled successfully")
        else:
            print("Room not found or already disabled")
    else:
        print("Room left active for testing.")


if __name__ == "__main__":
    test_100ms()
