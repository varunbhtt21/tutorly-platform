"""Mapper for InstructorProfile entity and SQLAlchemy InstructorProfile model."""

import json
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.domains.instructor.entities import InstructorProfile as DomainInstructorProfile
from app.domains.instructor.value_objects import (
    InstructorStatus,
    LanguageProficiency,
    Language,
    ProficiencyLevel,
    Pricing,
    Rating,
)
from app.infrastructure.persistence.sqlalchemy_models import InstructorProfile as SQLAlchemyInstructorProfile


class InstructorProfileMapper:
    """
    Maps between domain InstructorProfile entity and SQLAlchemy InstructorProfile model.

    Handles conversion of complex value objects:
    - LanguageProficiency (domain) <-> JSON string (database)
    - Pricing (domain) <-> separate numeric fields (database)
    - Rating (domain) <-> average_rating + total_ratings fields (database)
    - InstructorStatus enum conversion
    """

    @staticmethod
    def to_domain(db_instructor: SQLAlchemyInstructorProfile) -> DomainInstructorProfile:
        """
        Convert SQLAlchemy InstructorProfile to domain InstructorProfile entity.

        Args:
            db_instructor: SQLAlchemy InstructorProfile model instance

        Returns:
            Domain InstructorProfile entity
        """
        if db_instructor is None:
            return None

        # Convert languages JSON string to LanguageProficiency value object
        languages_spoken = None
        if db_instructor.languages:
            try:
                languages_data = json.loads(db_instructor.languages) if isinstance(db_instructor.languages, str) else db_instructor.languages
                languages = [
                    Language(
                        name=lang_dict["language"],
                        proficiency=ProficiencyLevel(lang_dict["proficiency"])
                    )
                    for lang_dict in languages_data
                ]
                languages_spoken = LanguageProficiency.create(languages)
            except (json.JSONDecodeError, KeyError, ValueError):
                # If parsing fails, leave as None
                languages_spoken = None

        # Convert pricing fields to Pricing value object
        pricing = None
        if db_instructor.regular_session_price is not None:
            pricing = Pricing(
                regular_session_price=Decimal(str(db_instructor.regular_session_price)),
                trial_session_price=Decimal(str(db_instructor.trial_session_price))
                if db_instructor.trial_session_price else None
            )

        # Convert rating fields to Rating value object
        rating = Rating.create(
            average_score=float(db_instructor.average_rating) if db_instructor.average_rating else 0.0,
            total_reviews=db_instructor.total_ratings or 0
        )

        return DomainInstructorProfile(
            id=db_instructor.id,
            user_id=db_instructor.user_id,
            status=InstructorStatus(db_instructor.status),
            languages_spoken=languages_spoken,
            pricing=pricing,
            rating=rating,
            country_of_birth=db_instructor.country_of_birth,
            profile_photo_url=db_instructor.profile_photo_url,
            bio=db_instructor.bio,
            teaching_experience=db_instructor.teaching_experience,
            headline=db_instructor.headline,
            intro_video_url=db_instructor.video_intro_url,
            intro_video_thumbnail_url=db_instructor.intro_video_thumbnail_url,
            onboarding_step=db_instructor.onboarding_step,
            is_onboarding_complete=db_instructor.is_onboarding_complete,
            total_sessions_completed=db_instructor.total_sessions,
            total_earnings=0.0,  # Not stored in ORM yet
            created_at=db_instructor.created_at,
            updated_at=db_instructor.updated_at,
        )

    @staticmethod
    def to_persistence(domain_instructor: DomainInstructorProfile) -> Dict[str, Any]:
        """
        Convert domain InstructorProfile entity to dict for SQLAlchemy update.

        Args:
            domain_instructor: Domain InstructorProfile entity

        Returns:
            Dict of field values for SQLAlchemy model
        """
        # Convert LanguageProficiency to JSON string
        languages_json = None
        if domain_instructor.languages_spoken:
            languages_list = [
                {
                    "language": lang.name,
                    "proficiency": lang.proficiency.value
                }
                for lang in domain_instructor.languages_spoken.languages
            ]
            languages_json = json.dumps(languages_list)

        # Extract pricing fields
        regular_price = None
        trial_price = None
        if domain_instructor.pricing:
            regular_price = float(domain_instructor.pricing.regular_session_price)
            trial_price = float(domain_instructor.pricing.trial_session_price) if domain_instructor.pricing.trial_session_price else None

        return {
            "user_id": domain_instructor.user_id,
            "country_of_birth": domain_instructor.country_of_birth,
            "languages": languages_json,
            "profile_photo_url": domain_instructor.profile_photo_url,
            "bio": domain_instructor.bio,
            "teaching_experience": domain_instructor.teaching_experience,
            "headline": domain_instructor.headline,
            "video_intro_url": domain_instructor.intro_video_url,
            "intro_video_thumbnail_url": domain_instructor.intro_video_thumbnail_url,
            "regular_session_price": regular_price,
            "trial_session_price": trial_price,
            "status": domain_instructor.status.value,
            "onboarding_step": domain_instructor.onboarding_step,
            "is_onboarding_complete": domain_instructor.is_onboarding_complete,
            "total_sessions": domain_instructor.total_sessions_completed,
            "average_rating": float(domain_instructor.rating.average_score),
            "total_ratings": domain_instructor.rating.total_reviews,
            "updated_at": domain_instructor.updated_at,
        }

    @staticmethod
    def create_orm_instance(domain_instructor: DomainInstructorProfile) -> SQLAlchemyInstructorProfile:
        """
        Create new SQLAlchemy InstructorProfile instance from domain InstructorProfile.

        Args:
            domain_instructor: Domain InstructorProfile entity

        Returns:
            SQLAlchemy InstructorProfile model instance
        """
        # Convert LanguageProficiency to JSON string
        languages_json = None
        if domain_instructor.languages_spoken:
            languages_list = [
                {
                    "language": lang.name,
                    "proficiency": lang.proficiency.value
                }
                for lang in domain_instructor.languages_spoken.languages
            ]
            languages_json = json.dumps(languages_list)

        # Extract pricing fields
        regular_price = None
        trial_price = None
        if domain_instructor.pricing:
            regular_price = float(domain_instructor.pricing.regular_session_price)
            trial_price = float(domain_instructor.pricing.trial_session_price) if domain_instructor.pricing.trial_session_price else None

        return SQLAlchemyInstructorProfile(
            user_id=domain_instructor.user_id,
            country_of_birth=domain_instructor.country_of_birth,
            languages=languages_json,
            profile_photo_url=domain_instructor.profile_photo_url,
            bio=domain_instructor.bio,
            teaching_experience=domain_instructor.teaching_experience,
            headline=domain_instructor.headline,
            video_intro_url=domain_instructor.intro_video_url,
            intro_video_thumbnail_url=domain_instructor.intro_video_thumbnail_url,
            regular_session_price=regular_price,
            trial_session_price=trial_price,
            status=domain_instructor.status.value,
            onboarding_step=domain_instructor.onboarding_step,
            is_onboarding_complete=domain_instructor.is_onboarding_complete,
            total_sessions=domain_instructor.total_sessions_completed,
            average_rating=float(domain_instructor.rating.average_score),
            total_ratings=domain_instructor.rating.total_reviews,
        )

    @staticmethod
    def update_orm_instance(
        db_instructor: SQLAlchemyInstructorProfile,
        domain_instructor: DomainInstructorProfile
    ) -> None:
        """
        Update SQLAlchemy InstructorProfile instance from domain InstructorProfile.

        Args:
            db_instructor: SQLAlchemy InstructorProfile model instance to update
            domain_instructor: Domain InstructorProfile entity with new values
        """
        # Convert LanguageProficiency to JSON string
        languages_json = None
        if domain_instructor.languages_spoken:
            languages_list = [
                {
                    "language": lang.name,
                    "proficiency": lang.proficiency.value
                }
                for lang in domain_instructor.languages_spoken.languages
            ]
            languages_json = json.dumps(languages_list)

        # Extract pricing fields
        regular_price = None
        trial_price = None
        if domain_instructor.pricing:
            regular_price = float(domain_instructor.pricing.regular_session_price)
            trial_price = float(domain_instructor.pricing.trial_session_price) if domain_instructor.pricing.trial_session_price else None

        db_instructor.country_of_birth = domain_instructor.country_of_birth
        db_instructor.languages = languages_json
        db_instructor.profile_photo_url = domain_instructor.profile_photo_url
        db_instructor.bio = domain_instructor.bio
        db_instructor.teaching_experience = domain_instructor.teaching_experience
        db_instructor.headline = domain_instructor.headline
        db_instructor.video_intro_url = domain_instructor.intro_video_url
        db_instructor.intro_video_thumbnail_url = domain_instructor.intro_video_thumbnail_url
        db_instructor.regular_session_price = regular_price
        db_instructor.trial_session_price = trial_price
        db_instructor.status = domain_instructor.status.value
        db_instructor.onboarding_step = domain_instructor.onboarding_step
        db_instructor.is_onboarding_complete = domain_instructor.is_onboarding_complete
        db_instructor.total_sessions = domain_instructor.total_sessions_completed
        db_instructor.average_rating = float(domain_instructor.rating.average_score)
        db_instructor.total_ratings = domain_instructor.rating.total_reviews
        db_instructor.updated_at = domain_instructor.updated_at
