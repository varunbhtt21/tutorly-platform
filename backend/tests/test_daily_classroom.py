"""
Test script for Daily.co classroom integration.

This script creates a test room and generates a meeting token to verify
that Daily.co is properly configured and working.

Usage:
    cd backend
    python -m tests.test_daily_classroom
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.dev")

from app.infrastructure.video_providers.daily_provider import DailyVideoProvider
from app.domains.classroom.services.video_provider import RoomConfig, ParticipantRole


def test_daily_co():
    """Test Daily.co room creation and token generation."""

    # Get credentials from environment
    api_key = os.getenv("DAILY_API_KEY")
    domain = os.getenv("DAILY_DOMAIN")

    if not api_key or not domain:
        print("❌ Error: DAILY_API_KEY and DAILY_DOMAIN must be set in .env.dev")
        print(f"   DAILY_API_KEY: {'Set' if api_key else 'Not set'}")
        print(f"   DAILY_DOMAIN: {'Set' if domain else 'Not set'}")
        return

    print(f"✅ Daily.co credentials found")
    print(f"   Domain: {domain}")
    print(f"   API Key: {api_key[:10]}...")
    print()

    # Initialize provider
    provider = DailyVideoProvider(api_key=api_key, domain=domain)

    # Create a test room
    test_session_id = 99999  # Dummy session ID for testing
    room_config = RoomConfig(
        session_id=test_session_id,
        instructor_id=1,
        student_id=2,
        scheduled_start=datetime.now(timezone.utc) + timedelta(minutes=5),
        duration_minutes=60,
    )

    print("📹 Creating test room...")
    try:
        room_info = provider.create_room(room_config)
        print(f"✅ Room created successfully!")
        print(f"   Room Name: {room_info.room_name}")
        print(f"   Room URL: {room_info.room_url}")
        print(f"   Expires At: {room_info.expires_at}")
        print()
    except Exception as e:
        print(f"❌ Failed to create room: {e}")
        return

    # Generate meeting token for instructor
    print("🎫 Generating meeting token for instructor...")
    try:
        instructor_token = provider.create_meeting_token(
            room_name=room_info.room_name,
            participant_id=1,
            participant_name="Test Instructor",
            participant_role=ParticipantRole.INSTRUCTOR,
            expires_in_minutes=120,
        )
        print(f"✅ Instructor token generated!")
        print(f"   Token (first 50 chars): {instructor_token.token[:50]}...")
        print()
    except Exception as e:
        print(f"❌ Failed to generate instructor token: {e}")
        return

    # Generate meeting token for student
    print("🎫 Generating meeting token for student...")
    try:
        student_token = provider.create_meeting_token(
            room_name=room_info.room_name,
            participant_id=2,
            participant_name="Test Student",
            participant_role=ParticipantRole.STUDENT,
            expires_in_minutes=120,
        )
        print(f"✅ Student token generated!")
        print(f"   Token (first 50 chars): {student_token.token[:50]}...")
        print()
    except Exception as e:
        print(f"❌ Failed to generate student token: {e}")
        return

    # Print join URLs
    print("=" * 60)
    print("🔗 JOIN URLS (Open these in your browser to test)")
    print("=" * 60)
    print()
    print("👨‍🏫 INSTRUCTOR JOIN URL:")
    print(f"   {instructor_token.room_url}")
    print()
    print("👨‍🎓 STUDENT JOIN URL:")
    print(f"   {student_token.room_url}")
    print()
    print("=" * 60)
    print("📝 Notes:")
    print("   - Open each URL in a different browser or incognito window")
    print("   - The room will expire in ~90 minutes")
    print("   - Both participants should be able to see and hear each other")
    print("=" * 60)

    # Cleanup option
    print()
    cleanup = input("Do you want to delete the test room? (y/n): ").lower().strip()
    if cleanup == 'y':
        print("🗑️ Deleting test room...")
        if provider.delete_room(room_info.room_name):
            print("✅ Room deleted successfully")
        else:
            print("⚠️ Room not found or already deleted")
    else:
        print("ℹ️ Room left active for testing. It will auto-expire.")


if __name__ == "__main__":
    test_daily_co()
