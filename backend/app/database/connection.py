"""
Database connection and session management.
Provides SQLAlchemy engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# Create database engine
# For SQLite, we use StaticPool and check_same_thread=False for development
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
else:
    # For PostgreSQL and other databases
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    Commits transaction on success, rolls back on exception.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit the transaction if no exceptions occurred
    except Exception:
        db.rollback()  # Rollback on any exception
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize the database.
    Creates all tables defined in models.

    Note: In production, use Alembic migrations instead of this.
    This is primarily for development and testing.
    """
    # Import all models here to ensure they're registered with Base
    from app.database import models

    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.
    USE WITH CAUTION - This will delete all data.
    Only use in development/testing.
    """
    if not settings.is_production:
        Base.metadata.drop_all(bind=engine)
    else:
        raise RuntimeError("Cannot drop database in production environment!")
