# Tutorly Platform Backend - Pure DDD Architecture

## Project Overview
Tutorly is an online tutoring marketplace (Preply-like) connecting instructors with students. The backend implements **Pure Domain-Driven Design (DDD)** with **Hexagonal Architecture** for maximum maintainability, testability, and scalability.

**Current Status**: ✅ Pure DDD architecture fully implemented - Ready for Phase 4+ development

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Architecture**: Pure DDD + Hexagonal Architecture (Ports & Adapters)
- **Package Management**: UV
- **Authentication**: JWT with role-based access control

## Pure DDD Architecture

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                 Presentation Layer (API)                     │
│              app/routers/ - API Controllers                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Uses
┌──────────────────────▼──────────────────────────────────────┐
│               Application Layer (Use Cases)                  │
│     app/application/use_cases/ - Business Workflows          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Orchestrates
┌──────────────────────▼──────────────────────────────────────┐
│                   Domain Layer (Core)                        │
│  app/domains/ - Entities, Value Objects, Events, Interfaces │
│              ⚠️ NO INFRASTRUCTURE DEPENDENCIES               │
└──────────────────────▲──────────────────────────────────────┘
                       │ Implemented by
┌──────────────────────┴──────────────────────────────────────┐
│              Infrastructure Layer (Adapters)                 │
│    app/infrastructure/ - DB, Mappers, Repository Impls       │
└─────────────────────────────────────────────────────────────┘
```

### 1. Domain Layer (`app/domains/`)
**Pure business logic - Zero infrastructure dependencies**

```
app/domains/
├── user/
│   ├── entities/
│   │   └── user.py                    # User aggregate with business logic
│   ├── value_objects/
│   │   ├── email.py                   # Validated, immutable Email
│   │   ├── password.py                # Password strength & hashing logic
│   │   ├── user_role.py               # STUDENT, INSTRUCTOR, ADMIN
│   │   └── user_status.py             # ACTIVE, INACTIVE, SUSPENDED, etc.
│   ├── events/
│   │   ├── user_registered.py
│   │   ├── email_verified.py
│   │   ├── password_changed.py
│   │   ├── user_status_changed.py
│   │   └── user_profile_updated.py
│   └── repositories/
│       └── user_repository.py         # IUserRepository interface (Port)
│
├── instructor/
│   ├── entities/
│   │   ├── instructor_profile.py      # Rich aggregate root
│   │   ├── education.py               # Education credential entity
│   │   └── experience.py              # Work experience entity
│   ├── value_objects/
│   │   ├── instructor_status.py       # DRAFT, PENDING_REVIEW, VERIFIED, etc.
│   │   ├── language_proficiency.py    # Language + ProficiencyLevel
│   │   ├── pricing.py                 # Session pricing with validation
│   │   └── rating.py                  # Rating score + review count
│   ├── events/
│   │   ├── instructor_onboarding_started.py
│   │   ├── instructor_onboarding_completed.py
│   │   ├── instructor_submitted_for_review.py
│   │   ├── instructor_verified.py
│   │   ├── instructor_rejected.py
│   │   ├── instructor_suspended.py
│   │   ├── pricing_updated.py
│   │   ├── profile_photo_updated.py
│   │   └── intro_video_updated.py
│   └── repositories/
│       ├── instructor_repository.py   # IInstructorProfileRepository
│       ├── education_repository.py    # IEducationRepository
│       └── experience_repository.py   # IExperienceRepository
│
├── student/
│   ├── entities/
│   │   └── student_profile.py
│   └── repositories/
│       └── student_repository.py
│
├── file/
│   ├── entities/
│   │   └── uploaded_file.py
│   ├── value_objects/
│   │   ├── file_type.py               # PROFILE_PHOTO, INTRO_VIDEO, etc.
│   │   └── file_status.py             # UPLOADING, COMPLETED, FAILED, DELETED
│   ├── events/
│   │   ├── file_uploaded.py
│   │   └── file_deleted.py
│   └── repositories/
│       └── file_repository.py
│
└── subject/
    ├── entities/
    │   ├── subject.py                 # Subject/topic entity
    │   └── instructor_subject.py      # Instructor-subject join
    └── repositories/
        ├── subject_repository.py
        └── instructor_subject_repository.py
```

### 2. Application Layer (`app/application/`)
**Use cases orchestrating domain logic**

```
app/application/use_cases/
├── user/
│   ├── register_user.py               # RegisterUserUseCase
│   ├── verify_email.py                # VerifyEmailUseCase
│   ├── login_user.py                  # LoginUserUseCase
│   └── update_user_profile.py         # UpdateUserProfileUseCase
│
├── instructor/
│   ├── create_instructor_profile.py
│   ├── update_instructor_about.py
│   ├── update_instructor_pricing.py
│   ├── complete_onboarding.py
│   ├── submit_for_review.py
│   ├── verify_instructor.py           # Admin action
│   ├── add_education.py
│   └── add_experience.py
│
├── student/
│   ├── create_student_profile.py
│   ├── update_student_profile.py
│   └── record_session_completion.py
│
└── file/
    ├── upload_file.py
    ├── delete_file.py
    ├── get_file.py
    └── list_user_files.py
```

### 3. Infrastructure Layer (`app/infrastructure/`)
**Adapters implementing domain contracts**

```
app/infrastructure/
├── persistence/
│   ├── sqlalchemy_models.py          # Re-export ORM models from app.models
│   └── mappers/                       # Domain ↔ ORM conversion
│       ├── user_mapper.py
│       ├── instructor_mapper.py
│       ├── student_mapper.py
│       ├── education_mapper.py
│       ├── experience_mapper.py
│       ├── file_mapper.py
│       ├── subject_mapper.py
│       └── instructor_subject_mapper.py
│
└── repositories/                       # Repository implementations (Adapters)
    ├── user_repository_impl.py        # SQLAlchemyUserRepository
    ├── instructor_repository_impl.py  # SQLAlchemyInstructorProfileRepository
    ├── student_repository_impl.py
    ├── education_repository_impl.py
    ├── experience_repository_impl.py
    ├── file_repository_impl.py
    ├── subject_repository_impl.py
    └── instructor_subject_repository_impl.py
```

### 4. Presentation Layer (`app/routers/`)
**API Controllers**

```
app/routers/
├── auth.py            # Authentication endpoints (register, login, verify)
├── instructor.py      # Instructor onboarding and management
├── upload.py          # File upload endpoints
└── (more routers to be added in future phases)
```

### 5. Core (`app/core/`)
**Configuration & Cross-cutting Concerns**

```
app/core/
├── config.py          # Application settings
├── dependencies.py    # FastAPI dependency injection (repositories, use cases)
├── security.py        # JWT, password hashing
└── exceptions.py      # Custom domain exceptions
```

## Pure DDD Principles

### 1. Ubiquitous Language
Code uses business language, not technical jargon:

```python
# ✅ Good - Business language
instructor_profile.submit_for_review()
user.verify_email()
pricing.calculate_session_price(is_trial=True)

# ❌ Bad - Technical language
instructor_profile.set_status("pending_review")
user.email_verified = True
price = pricing.trial_price if is_trial else pricing.regular_price
```

### 2. Rich Domain Models
Entities contain business logic, not just data:

```python
# ✅ Good - Rich domain model
class User:
    def verify_email(self) -> None:
        if self.email_verified:
            raise ValueError("Email already verified")
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
        self.status = UserStatus.ACTIVE
        self._add_domain_event(EmailVerified(...))

# ❌ Bad - Anemic domain model
class User:
    email_verified: bool
    email_verified_at: datetime
    status: str
```

### 3. Value Objects
Immutable objects with validation:

```python
# Email value object
email = Email("john@example.com")  # Validates format, normalizes to lowercase
print(email.domain)  # "example.com"
print(email.local_part)  # "john"

# Password value object
password = Password.create_from_plain("SecurePass123!", hasher_func)  # Validates strength
password.verify("SecurePass123!", verifier_func)  # True

# Pricing value object
pricing = Pricing.create(regular_price=50.0, trial_price=25.0)  # Validates constraints
price = pricing.calculate_session_price(is_trial=True)  # 25.0
```

### 4. Domain Events
Events communicate state changes:

```python
# When user registers
user = User.register(email, password, first_name, last_name, role)
events = user.get_domain_events()
# [UserRegistered(user_id=1, email="john@example.com", role=STUDENT)]

# Can trigger:
# - Send welcome email
# - Create initial preferences
# - Log analytics event
```

### 5. Repository Pattern (Ports & Adapters)

**Port (Domain Layer)** - Abstract interface:
```python
# app/domains/user/repositories/user_repository.py
class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        pass
```

**Adapter (Infrastructure Layer)** - Concrete implementation:
```python
# app/infrastructure/repositories/user_repository_impl.py
class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        db_user = UserMapper.create_orm_instance(user)
        self.db.add(db_user)
        self.db.commit()
        return UserMapper.to_domain(db_user)
```

### 6. Dependency Inversion
High-level modules depend on abstractions, not implementations:

```python
# Use case depends on interface (Port), not implementation
class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository):  # ← Interface
        self.user_repo = user_repo

# FastAPI provides implementation (Adapter) via dependency injection
def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return SQLAlchemyUserRepository(db)  # ← Implementation
```

## Data Flow Example

**Register New User Flow:**

```
1. Presentation Layer (auth.py)
   ↓ POST /auth/register
   use_case.execute(email, password, first_name, last_name, role)

2. Application Layer (register_user.py)
   ↓ Create value objects
   email_vo = Email(email)
   password_vo = Password.create_from_plain(password, hasher)
   ↓ Use domain factory
   user = User.register(email_vo, password_vo, ...)
   ↓ Save via repository
   saved_user = user_repo.save(user)

3. Domain Layer (user.py)
   ↓ Factory method
   @classmethod
   def register(cls, email, password, ...):
       user = cls(email=email, password=password, status=INACTIVE, ...)
       user._add_domain_event(UserRegistered(...))
       return user

4. Infrastructure Layer (user_repository_impl.py)
   ↓ Map domain entity to ORM
   db_user = UserMapper.create_orm_instance(user)
   ↓ Save to database
   db.add(db_user)
   db.commit()
   ↓ Map ORM back to domain entity
   return UserMapper.to_domain(db_user)
```

## Key Domain Entities

### User Domain
- **User** - Authentication, authorization, profile management
- **Email** - Validated, normalized email address
- **Password** - Strength validation, secure hashing
- **UserRole** - STUDENT, INSTRUCTOR, ADMIN
- **UserStatus** - ACTIVE, INACTIVE, SUSPENDED, BANNED, DELETED

### Instructor Domain
- **InstructorProfile** - Instructor lifecycle (onboarding, verification, suspension)
- **Education** - Education credentials
- **Experience** - Work experience
- **Pricing** - Session pricing (regular: $5-200, trial: $1-100)
- **Rating** - Average rating (0-5 stars) + review count
- **LanguageProficiency** - Languages spoken with proficiency levels
- **InstructorStatus** - DRAFT, PENDING_REVIEW, VERIFIED, REJECTED, SUSPENDED

### Student Domain
- **StudentProfile** - Learning goals, preferences, session statistics

### File Domain
- **UploadedFile** - File metadata, lifecycle, optimization status
- **FileType** - PROFILE_PHOTO, INTRO_VIDEO, CERTIFICATE, DOCUMENT
- **FileStatus** - UPLOADING, COMPLETED, FAILED, DELETED

### Subject Domain
- **Subject** - Subjects/topics available for tutoring
- **InstructorSubject** - Instructor expertise in subjects (years of experience)

## Development Workflow

### Adding New Feature (Pure DDD Approach)

**Example: Add "Mark Instructor as Featured" Feature**

**1. Domain Layer** - Business logic in entity:
```python
# app/domains/instructor/entities/instructor_profile.py
def mark_as_featured(self) -> None:
    if not self.is_verified:
        raise ValueError("Only verified instructors can be featured")
    self.is_featured = True
    self.updated_at = datetime.utcnow()
    self._add_domain_event(InstructorFeatured(instructor_id=self.id))
```

**2. Application Layer** - Use case:
```python
# app/application/use_cases/instructor/mark_as_featured.py
class MarkInstructorAsFeaturedUseCase:
    def __init__(self, instructor_repo: IInstructorProfileRepository):
        self.instructor_repo = instructor_repo

    def execute(self, instructor_id: int) -> InstructorProfile:
        instructor = self.instructor_repo.get_by_id(instructor_id)
        if not instructor:
            raise ValueError("Instructor not found")
        instructor.mark_as_featured()
        return self.instructor_repo.update(instructor)
```

**3. Presentation Layer** - API endpoint:
```python
# app/routers/admin.py
@router.post("/instructors/{instructor_id}/feature")
async def mark_instructor_featured(
    instructor_id: int,
    use_case: MarkInstructorAsFeaturedUseCase = Depends(get_mark_as_featured_use_case),
    current_user: User = Depends(get_current_admin)
):
    instructor = use_case.execute(instructor_id)
    return {"message": "Instructor marked as featured", "instructor_id": instructor.id}
```

**4. Dependencies** - Dependency injection:
```python
# app/core/dependencies.py
def get_mark_as_featured_use_case(
    instructor_repo: IInstructorProfileRepository = Depends(get_instructor_repository)
) -> MarkInstructorAsFeaturedUseCase:
    return MarkInstructorAsFeaturedUseCase(instructor_repo)
```

## Benefits of Pure DDD

### 1. Testability
```python
# Domain tests - No database needed
def test_instructor_submission():
    instructor = InstructorProfile.create_for_user(user_id=1)
    instructor.complete_onboarding()
    instructor.submit_for_review()
    assert instructor.status == InstructorStatus.PENDING_REVIEW
    assert len(instructor.get_domain_events()) == 3
```

### 2. Maintainability
- Business logic centralized in domain
- Clear separation of concerns
- Easy to understand and modify

### 3. Scalability
- Can swap SQLAlchemy for another ORM without touching domain
- Can add new use cases without modifying domain
- Microservices-ready

### 4. Business Alignment
- Code reflects business language
- Domain experts can validate domain code
- Requirements map directly to code

## Running the Application

```bash
# Development mode
python run_server.py

# Production mode
python run_server.py --prod

# Custom host/port
python run_server.py --host 0.0.0.0 --port 8080
```

## Current Implementation Status

### ✅ Completed Phases

**Phase 1: Authentication** (COMPLETED)
- User registration with role selection
- JWT-based authentication
- Email verification
- Password management

**Phase 2: Instructor Onboarding** (COMPLETED)
- 7-step onboarding process
- Profile creation and management
- Education and experience tracking
- Subject selection
- Pricing configuration

**Phase 3: File Upload & Storage** (COMPLETED)
- Profile photo upload with optimization
- Intro video upload
- Document upload (certificates, diplomas)
- Thumbnail generation
- Local filesystem storage (can migrate to S3)

**✅ Pure DDD Refactoring** (COMPLETED)
- All domains implemented with Pure DDD
- Use cases for all operations
- Infrastructure layer with mappers
- Repository pattern (ports & adapters)
- Domain events

### 📊 Statistics
- **Total Endpoints**: 28 RESTful API endpoints
- **Domains**: 5 (User, Instructor, Student, File, Subject)
- **Use Cases**: 20+ application use cases
- **Repository Implementations**: 8 SQLAlchemy repositories
- **Architecture**: Pure DDD + Hexagonal

### 📂 File Structure Summary
```
backend/
├── app/
│   ├── domains/               # 📁 Domain Layer (5 domains)
│   ├── application/           # 📁 Application Layer (20+ use cases)
│   ├── infrastructure/        # 📁 Infrastructure Layer (8 repos, 8 mappers)
│   ├── routers/               # 📁 Presentation Layer (3 routers)
│   ├── core/                  # 📁 Config, dependencies, security
│   ├── database/              # 📁 DB connection
│   └── utils/                 # 📁 Utilities
├── app/_old_implementation_backup/  # 📁 Old code (models, services, etc.)
├── run_server.py
├── pyproject.toml
└── CLAUDE.md                  # 📄 This file
```

## Next Development Steps

### Phase 4: Student Profile & Search (NEXT)
- Student profile management
- Instructor search with filters
- Public instructor profiles
- Availability display

### Phase 5: Session Booking System
- Availability calendar management
- Booking flow
- Payment integration (Stripe)
- Session confirmation

### Phase 6: Real-time Messaging
- Pre-booking chat (restricted)
- Post-booking chat (full features)
- Violation detection
- File sharing

### Phase 7: Session Management
- Session lifecycle
- Google Meet integration
- Session reminders
- Completion confirmation

### Phase 8: Payment & Wallet
- Payment processing
- Instructor wallet
- Withdrawal management
- Refund handling

### Phase 9: Reviews & Ratings
- Student reviews
- Rating system
- Instructor responses

### Phase 10: Admin Dashboard
- Instructor verification
- Content moderation
- Analytics
- Dispute resolution

## Migration Notes

### Old Implementation Backup
Old code backed up in `app/_old_implementation_backup/`:
- `models/` - Old SQLAlchemy-centric models
- `repositories/` - Old repository pattern
- `services/` - Old service layer
- `schemas/` - Old Pydantic schemas

### What Changed
- ❌ Anemic domain models → ✅ Rich domain entities
- ❌ Services with business logic → ✅ Domain entities with business logic
- ❌ Direct ORM dependencies → ✅ Repository interfaces (ports)
- ❌ Scattered validation → ✅ Value objects with validation
- ❌ No domain events → ✅ Domain events for integration

## Resources

- **Domain-Driven Design** by Eric Evans (Blue Book)
- **Implementing Domain-Driven Design** by Vaughn Vernon (Red Book)
- **Clean Architecture** by Robert C. Martin
- **Hexagonal Architecture** by Alistair Cockburn
- **Patterns of Enterprise Application Architecture** by Martin Fowler

---

**Architecture**: Pure DDD + Hexagonal
**Status**: Production-ready foundation
**Next**: Phase 4 - Student Profile & Search
