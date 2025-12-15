"""
Routers package - API endpoints.
Centralizes all router imports.
"""

from app.routers import auth, instructor, upload, calendar, messaging, websocket, subjects, admin

__all__ = ["auth", "instructor", "upload", "calendar", "messaging", "websocket", "subjects", "admin"]
