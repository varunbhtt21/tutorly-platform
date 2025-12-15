"""
Subjects REST API Router.

Provides endpoints for fetching available subjects.
Public endpoint - no authentication required.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Subject


router = APIRouter(prefix="/subjects", tags=["subjects"])


# ============================================================================
# Response Schemas
# ============================================================================

class SubjectResponse(BaseModel):
    """Subject response schema."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectListResponse(BaseModel):
    """List of subjects response."""
    subjects: List[SubjectResponse]
    total: int


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=SubjectListResponse)
async def get_subjects(
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Only return active subjects"),
    db: Session = Depends(get_db),
):
    """
    Get all available subjects.

    This is a public endpoint - no authentication required.
    Returns subjects from the database for use in filters and dropdowns.
    """
    query = db.query(Subject)

    if active_only:
        query = query.filter(Subject.is_active == True)

    if category:
        query = query.filter(Subject.category == category)

    # Order alphabetically by name
    subjects = query.order_by(Subject.name).all()

    return SubjectListResponse(
        subjects=[
            SubjectResponse(
                id=s.id,
                name=s.name,
                slug=s.slug,
                description=s.description,
                category=s.category,
            )
            for s in subjects
        ],
        total=len(subjects),
    )


@router.get("/categories", response_model=List[str])
async def get_subject_categories(
    db: Session = Depends(get_db),
):
    """
    Get all unique subject categories.

    Returns a list of distinct category names for filtering.
    """
    categories = (
        db.query(Subject.category)
        .filter(Subject.is_active == True)
        .filter(Subject.category.isnot(None))
        .distinct()
        .all()
    )

    return sorted([c[0] for c in categories if c[0]])


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific subject by ID."""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()

    if not subject:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )

    return SubjectResponse(
        id=subject.id,
        name=subject.name,
        slug=subject.slug,
        description=subject.description,
        category=subject.category,
    )
