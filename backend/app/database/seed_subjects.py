"""
Seed script for initial subject data.

Populates the database with common subjects across different categories.
Run this once during initial setup or when needed to refresh subject data.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.subject import SubjectCategory
from app.repositories.subject_repository import SubjectRepository


# Initial subject data organized by category
INITIAL_SUBJECTS: List[Dict[str, Any]] = [
    # ===== LANGUAGES =====
    {"name": "English", "category": SubjectCategory.LANGUAGES},
    {"name": "Spanish", "category": SubjectCategory.LANGUAGES},
    {"name": "French", "category": SubjectCategory.LANGUAGES},
    {"name": "German", "category": SubjectCategory.LANGUAGES},
    {"name": "Italian", "category": SubjectCategory.LANGUAGES},
    {"name": "Portuguese", "category": SubjectCategory.LANGUAGES},
    {"name": "Russian", "category": SubjectCategory.LANGUAGES},
    {"name": "Chinese (Mandarin)", "category": SubjectCategory.LANGUAGES},
    {"name": "Japanese", "category": SubjectCategory.LANGUAGES},
    {"name": "Korean", "category": SubjectCategory.LANGUAGES},
    {"name": "Arabic", "category": SubjectCategory.LANGUAGES},
    {"name": "Hindi", "category": SubjectCategory.LANGUAGES},
    {"name": "Turkish", "category": SubjectCategory.LANGUAGES},
    {"name": "Dutch", "category": SubjectCategory.LANGUAGES},
    {"name": "Polish", "category": SubjectCategory.LANGUAGES},

    # ===== PROGRAMMING =====
    {"name": "Python", "category": SubjectCategory.PROGRAMMING},
    {"name": "JavaScript", "category": SubjectCategory.PROGRAMMING},
    {"name": "Java", "category": SubjectCategory.PROGRAMMING},
    {"name": "C++", "category": SubjectCategory.PROGRAMMING},
    {"name": "C#", "category": SubjectCategory.PROGRAMMING},
    {"name": "Ruby", "category": SubjectCategory.PROGRAMMING},
    {"name": "PHP", "category": SubjectCategory.PROGRAMMING},
    {"name": "Swift", "category": SubjectCategory.PROGRAMMING},
    {"name": "Kotlin", "category": SubjectCategory.PROGRAMMING},
    {"name": "Go", "category": SubjectCategory.PROGRAMMING},
    {"name": "Rust", "category": SubjectCategory.PROGRAMMING},
    {"name": "TypeScript", "category": SubjectCategory.PROGRAMMING},
    {"name": "SQL", "category": SubjectCategory.PROGRAMMING},
    {"name": "HTML/CSS", "category": SubjectCategory.PROGRAMMING},
    {"name": "React", "category": SubjectCategory.PROGRAMMING},
    {"name": "Node.js", "category": SubjectCategory.PROGRAMMING},
    {"name": "Django", "category": SubjectCategory.PROGRAMMING},
    {"name": "Flutter", "category": SubjectCategory.PROGRAMMING},

    # ===== ARTS (Music, Design, Creative) =====
    {"name": "Piano", "category": SubjectCategory.ARTS},
    {"name": "Guitar", "category": SubjectCategory.ARTS},
    {"name": "Violin", "category": SubjectCategory.ARTS},
    {"name": "Drums", "category": SubjectCategory.ARTS},
    {"name": "Singing/Vocals", "category": SubjectCategory.ARTS},
    {"name": "Music Theory", "category": SubjectCategory.ARTS},
    {"name": "Drawing", "category": SubjectCategory.ARTS},
    {"name": "Painting", "category": SubjectCategory.ARTS},
    {"name": "Graphic Design", "category": SubjectCategory.ARTS},
    {"name": "UI/UX Design", "category": SubjectCategory.ARTS},
    {"name": "Photography", "category": SubjectCategory.ARTS},
    {"name": "Video Editing", "category": SubjectCategory.ARTS},
    {"name": "Animation", "category": SubjectCategory.ARTS},

    # ===== MATHEMATICS =====
    {"name": "Algebra", "category": SubjectCategory.MATHEMATICS},
    {"name": "Geometry", "category": SubjectCategory.MATHEMATICS},
    {"name": "Calculus", "category": SubjectCategory.MATHEMATICS},
    {"name": "Statistics", "category": SubjectCategory.MATHEMATICS},
    {"name": "Trigonometry", "category": SubjectCategory.MATHEMATICS},
    {"name": "Linear Algebra", "category": SubjectCategory.MATHEMATICS},
    {"name": "Discrete Mathematics", "category": SubjectCategory.MATHEMATICS},

    # ===== SCIENCES =====
    {"name": "Physics", "category": SubjectCategory.SCIENCES},
    {"name": "Chemistry", "category": SubjectCategory.SCIENCES},
    {"name": "Biology", "category": SubjectCategory.SCIENCES},
    {"name": "Environmental Science", "category": SubjectCategory.SCIENCES},
    {"name": "Astronomy", "category": SubjectCategory.SCIENCES},
    {"name": "Computer Science", "category": SubjectCategory.SCIENCES},
    {"name": "Psychology", "category": SubjectCategory.SCIENCES},

    # ===== BUSINESS =====
    {"name": "Business Management", "category": SubjectCategory.BUSINESS},
    {"name": "Marketing", "category": SubjectCategory.BUSINESS},
    {"name": "Accounting", "category": SubjectCategory.BUSINESS},
    {"name": "Finance", "category": SubjectCategory.BUSINESS},
    {"name": "Entrepreneurship", "category": SubjectCategory.BUSINESS},
    {"name": "Project Management", "category": SubjectCategory.BUSINESS},
    {"name": "Economics", "category": SubjectCategory.BUSINESS},
    {"name": "Human Resources", "category": SubjectCategory.BUSINESS},
    {"name": "Business Analytics", "category": SubjectCategory.BUSINESS},

    # ===== TEST PREPARATION =====
    {"name": "SAT Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "ACT Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "GRE Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "GMAT Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "TOEFL Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "IELTS Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "MCAT Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "LSAT Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "AP Exam Prep", "category": SubjectCategory.TEST_PREP},
    {"name": "IB Exam Prep", "category": SubjectCategory.TEST_PREP},

    # ===== OTHER =====
    {"name": "History", "category": SubjectCategory.OTHER},
    {"name": "Geography", "category": SubjectCategory.OTHER},
    {"name": "Literature", "category": SubjectCategory.OTHER},
    {"name": "Philosophy", "category": SubjectCategory.OTHER},
    {"name": "Political Science", "category": SubjectCategory.OTHER},
    {"name": "Sociology", "category": SubjectCategory.OTHER},
    {"name": "Cooking", "category": SubjectCategory.OTHER},
    {"name": "Public Speaking", "category": SubjectCategory.OTHER},
    {"name": "Leadership", "category": SubjectCategory.OTHER},
    {"name": "Yoga", "category": SubjectCategory.OTHER},
    {"name": "Fitness Training", "category": SubjectCategory.OTHER},
]


def seed_subjects(db: Session) -> None:
    """
    Seed the database with initial subject data.

    Args:
        db: Database session

    Returns:
        None
    """
    print("🌱 Starting subject seeding...")

    subject_repo = SubjectRepository(db)

    # Bulk create subjects
    created_subjects = subject_repo.bulk_create_subjects(INITIAL_SUBJECTS)

    print(f"✅ Successfully seeded {len(created_subjects)} subjects")

    # Print summary by category
    categories = {}
    for subject in created_subjects:
        cat = subject.category.value
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📊 Subjects by category:")
    for category, count in sorted(categories.items()):
        print(f"  • {category}: {count} subjects")

    print("\n✅ Subject seeding completed!")


def get_seed_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics about seeded subjects.

    Args:
        db: Database session

    Returns:
        Dictionary with seed statistics
    """
    subject_repo = SubjectRepository(db)

    total_subjects = len(subject_repo.get_all())

    by_category = {}
    for category in SubjectCategory:
        count = len(subject_repo.get_by_category(category))
        by_category[category.value] = count

    return {
        "total_subjects": total_subjects,
        "by_category": by_category,
        "categories_count": len([c for c in by_category.values() if c > 0])
    }


if __name__ == "__main__":
    """Run seeding as a standalone script."""
    from app.database.connection import SessionLocal

    print("=" * 70)
    print("TUTORLY PLATFORM - SUBJECT SEEDING SCRIPT")
    print("=" * 70)
    print()

    db = SessionLocal()
    try:
        seed_subjects(db)

        # Print statistics
        print("\n" + "=" * 70)
        stats = get_seed_statistics(db)
        print(f"Total subjects in database: {stats['total_subjects']}")
        print(f"Active categories: {stats['categories_count']}")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()
