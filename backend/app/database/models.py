"""
SQLAlchemy ORM Models for Database Persistence.

These are the ORM models (database schema) separate from domain entities.
In Pure DDD, these live in the infrastructure layer and are mapped to domain entities via mappers.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Numeric,
    ForeignKey, Enum as SQLEnum, Table
)
from sqlalchemy.orm import relationship
import enum

from app.database.connection import Base


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """User account status."""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class InstructorStatus(str, enum.Enum):
    """Instructor profile status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class ProficiencyLevel(str, enum.Enum):
    """Language proficiency level."""
    NATIVE = "native"
    FLUENT = "fluent"
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"


class FileType(str, enum.Enum):
    """Uploaded file type."""
    PROFILE_PHOTO = "profile_photo"
    INTRO_VIDEO = "intro_video"
    CERTIFICATE = "certificate"
    DOCUMENT = "document"


class FileStatus(str, enum.Enum):
    """File upload status."""
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


# ============================================================================
# ORM Models
# ============================================================================

class User(Base):
    """User ORM model (maps to users table)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING_VERIFICATION)

    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)

    # Email verification
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    is_phone_verified = Column(Boolean, default=False, nullable=False)

    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    violation_count = Column(Integer, default=0, nullable=False)
    last_violation_at = Column(DateTime, nullable=True)

    # Settings
    timezone = Column(String(50), default='UTC', nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    instructor_profile = relationship("InstructorProfile", back_populates="user", foreign_keys="[InstructorProfile.user_id]", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="user", foreign_keys="[UploadedFile.uploaded_by]", cascade="all, delete-orphan")


class InstructorProfile(Base):
    """Instructor profile ORM model."""

    __tablename__ = "instructor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(SQLEnum(InstructorStatus), nullable=False, default=InstructorStatus.DRAFT)

    # About section (Step 1)
    country_of_birth = Column(String(100), nullable=True)
    languages = Column(Text, nullable=True)  # JSON string of languages

    # Profile media
    profile_photo_url = Column(String(500), nullable=True)

    # Description section (Step 2)
    headline = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    teaching_experience = Column(Text, nullable=True)

    # Pricing section (Step 3)
    regular_session_price = Column(Numeric(10, 2), nullable=True)
    trial_session_price = Column(Numeric(10, 2), nullable=True)

    # Video introduction
    video_intro_url = Column(String(500), nullable=True)
    intro_video_thumbnail_url = Column(String(500), nullable=True)

    # Rating and stats
    average_rating = Column(Numeric(3, 2), nullable=True, default=Decimal("0.00"))
    total_ratings = Column(Integer, nullable=False, default=0)
    total_sessions = Column(Integer, nullable=False, default=0)

    # Onboarding completion tracking
    onboarding_step = Column(Integer, nullable=False, default=1)
    is_onboarding_complete = Column(Boolean, nullable=False, default=False)
    onboarding_completed_at = Column(DateTime, nullable=True)

    # Verification
    verified_at = Column(DateTime, nullable=True)
    verified_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="instructor_profile", foreign_keys=[user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_admin_id])
    education = relationship("Education", back_populates="instructor_profile", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="instructor_profile", cascade="all, delete-orphan")
    instructor_subjects = relationship("InstructorSubject", back_populates="instructor_profile", cascade="all, delete-orphan")


class StudentProfile(Base):
    """Student profile ORM model."""

    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Student preferences
    learning_goals = Column(Text, nullable=True)
    preferred_learning_style = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")


class Education(Base):
    """Education record ORM model."""

    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    instructor_profile_id = Column(Integer, ForeignKey("instructor_profiles.id", ondelete="CASCADE"), nullable=False)

    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=False)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor_profile = relationship("InstructorProfile", back_populates="education")


class Experience(Base):
    """Work experience ORM model."""

    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    instructor_profile_id = Column(Integer, ForeignKey("instructor_profiles.id", ondelete="CASCADE"), nullable=False)

    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor_profile = relationship("InstructorProfile", back_populates="experience")


class Subject(Base):
    """Subject/course ORM model."""

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor_subjects = relationship("InstructorSubject", back_populates="subject", cascade="all, delete-orphan")


class InstructorSubject(Base):
    """Instructor-Subject relationship (many-to-many with extra fields)."""

    __tablename__ = "instructor_subjects"

    id = Column(Integer, primary_key=True, index=True)
    instructor_profile_id = Column(Integer, ForeignKey("instructor_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    # Proficiency and experience with this subject
    years_of_experience = Column(Integer, nullable=True)
    proficiency_level = Column(SQLEnum(ProficiencyLevel), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    instructor_profile = relationship("InstructorProfile", back_populates="instructor_subjects")
    subject = relationship("Subject", back_populates="instructor_subjects")


class UploadedFile(Base):
    """Uploaded file ORM model."""

    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructor_profiles.id", ondelete="SET NULL"), nullable=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True)

    # File metadata
    file_type = Column(SQLEnum(FileType), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    storage_backend = Column(String(50), nullable=False, default="local")

    # Status and processing
    status = Column(SQLEnum(FileStatus), nullable=False, default=FileStatus.UPLOADING)
    is_optimized = Column(Boolean, nullable=False, default=False)

    # URLs
    public_url = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="uploaded_files", foreign_keys=[uploaded_by])


# ============================================================================
# Scheduling Models
# ============================================================================

class AvailabilitySlot(Base):
    """Instructor availability slot ORM model."""

    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type: 'recurring' or 'one_time'
    availability_type = Column(String(20), nullable=False)

    # For recurring availability (0=Monday, 6=Sunday)
    day_of_week = Column(Integer, nullable=True)

    # Time window
    start_time = Column(String(10), nullable=False)  # HH:MM format
    end_time = Column(String(10), nullable=False)    # HH:MM format

    # For one-time availability
    specific_date = Column(String(10), nullable=True)  # YYYY-MM-DD format

    # Slot configuration
    slot_duration_minutes = Column(Integer, default=50)
    break_minutes = Column(Integer, default=10)

    # Validity period for recurring
    valid_from = Column(String(10), nullable=False)  # YYYY-MM-DD
    valid_until = Column(String(10), nullable=True)  # YYYY-MM-DD

    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    """Booked tutoring session ORM model."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Timing
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    timezone = Column(String(50), default="UTC")

    # Type and status
    session_type = Column(String(20), nullable=False)  # trial, single, recurring
    status = Column(String(30), nullable=False, default="pending_confirmation")

    # Recurrence (for weekly lessons)
    parent_session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    recurrence_pattern = Column(String(20), nullable=True)  # 'weekly'
    occurrence_number = Column(Integer, default=1)

    # Subject and pricing
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")

    # Notes and meeting
    instructor_notes = Column(Text, nullable=True)
    student_notes = Column(Text, nullable=True)
    meeting_link = Column(String(500), nullable=True)

    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = relationship("Session", backref="parent", remote_side=[id])


class BookingSlot(Base):
    """Individual bookable time slot ORM model."""

    __tablename__ = "booking_slots"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Reference to the availability rule that created this slot (optional)
    availability_rule_id = Column(
        Integer,
        ForeignKey("availability_slots.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Exact timing for this slot
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=50)

    # Status: available, booked, blocked
    status = Column(String(20), nullable=False, default="available")

    # If booked, link to the session
    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TimeOff(Base):
    """Instructor time off / blocked time ORM model."""

    __tablename__ = "time_off"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer,
        ForeignKey("instructor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)

    # For recurring weekly blocks
    is_recurring = Column(Boolean, default=False)
    recurrence_day = Column(Integer, nullable=True)  # 0=Monday, 6=Sunday

    created_at = Column(DateTime, default=datetime.utcnow)
