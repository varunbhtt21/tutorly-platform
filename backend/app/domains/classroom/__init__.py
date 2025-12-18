"""
Classroom Domain.

This domain handles video classroom functionality for tutoring sessions.
It provides an abstraction over video providers (Daily.co, Twilio, etc.)
making it easy to switch providers without changing application code.

Domain Components:
- Entities: ClassroomSession (links session to video room)
- Value Objects: RoomStatus
- Services: IVideoProvider (port for video providers)
- Repositories: IClassroomRepository (room persistence)

Key Features:
- Provider-agnostic design (Ports & Adapters pattern)
- Room lifecycle management
- Participant authentication with tokens
- Session-based room access control
"""
