"""
SQLAlchemy implementation of the Classroom Repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domains.classroom.repositories import IClassroomRepository
from app.domains.classroom.entities import ClassroomSession
from app.domains.classroom.value_objects import RoomStatus
from app.infrastructure.persistence.models.classroom_models import ClassroomSessionModel


class ClassroomRepositoryImpl(IClassroomRepository):
    """SQLAlchemy implementation of IClassroomRepository."""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: ClassroomSessionModel) -> ClassroomSession:
        """Convert SQLAlchemy model to domain entity."""
        return ClassroomSession(
            id=model.id,
            session_id=model.session_id,
            instructor_id=model.instructor_id,
            student_id=model.student_id,
            room_id=model.room_id,
            room_name=model.room_name,
            room_url=model.room_url,
            provider=model.provider,
            status=RoomStatus(model.status),
            created_at=model.created_at,
            expires_at=model.expires_at,
            started_at=model.started_at,
            ended_at=model.ended_at,
        )

    def _to_model(self, entity: ClassroomSession) -> ClassroomSessionModel:
        """Convert domain entity to SQLAlchemy model."""
        model = ClassroomSessionModel(
            session_id=entity.session_id,
            instructor_id=entity.instructor_id,
            student_id=entity.student_id,
            room_id=entity.room_id,
            room_name=entity.room_name,
            room_url=entity.room_url,
            provider=entity.provider,
            status=entity.status.value,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            started_at=entity.started_at,
            ended_at=entity.ended_at,
        )
        if entity.id:
            model.id = entity.id
        return model

    def save(self, classroom: ClassroomSession) -> ClassroomSession:
        """Save a classroom session."""
        if classroom.id:
            # Update existing
            model = self.db.query(ClassroomSessionModel).filter(
                ClassroomSessionModel.id == classroom.id
            ).first()
            if model:
                model.status = classroom.status.value
                model.room_id = classroom.room_id
                model.room_name = classroom.room_name
                model.room_url = classroom.room_url
                model.started_at = classroom.started_at
                model.ended_at = classroom.ended_at
                model.expires_at = classroom.expires_at
                self.db.commit()
                self.db.refresh(model)
                return self._to_entity(model)

        # Create new
        model = self._to_model(classroom)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, classroom_id: int) -> Optional[ClassroomSession]:
        """Get by ID."""
        model = self.db.query(ClassroomSessionModel).filter(
            ClassroomSessionModel.id == classroom_id
        ).first()
        return self._to_entity(model) if model else None

    def get_by_session_id(self, session_id: int) -> Optional[ClassroomSession]:
        """Get by tutoring session ID."""
        model = self.db.query(ClassroomSessionModel).filter(
            ClassroomSessionModel.session_id == session_id
        ).first()
        return self._to_entity(model) if model else None

    def get_by_room_name(self, room_name: str) -> Optional[ClassroomSession]:
        """Get by room name."""
        model = self.db.query(ClassroomSessionModel).filter(
            ClassroomSessionModel.room_name == room_name
        ).first()
        return self._to_entity(model) if model else None

    def get_active_for_user(self, user_id: int) -> List[ClassroomSession]:
        """Get active classrooms for a user."""
        active_statuses = [RoomStatus.CREATED.value, RoomStatus.ACTIVE.value]
        models = self.db.query(ClassroomSessionModel).filter(
            or_(
                ClassroomSessionModel.instructor_id == user_id,
                ClassroomSessionModel.student_id == user_id
            ),
            ClassroomSessionModel.status.in_(active_statuses)
        ).all()
        return [self._to_entity(m) for m in models]

    def update_status(self, classroom_id: int, status: RoomStatus) -> bool:
        """Update classroom status."""
        result = self.db.query(ClassroomSessionModel).filter(
            ClassroomSessionModel.id == classroom_id
        ).update({"status": status.value})
        self.db.commit()
        return result > 0

    def delete(self, classroom_id: int) -> bool:
        """Delete a classroom record."""
        result = self.db.query(ClassroomSessionModel).filter(
            ClassroomSessionModel.id == classroom_id
        ).delete()
        self.db.commit()
        return result > 0
