# Tutorly Platform - Backend

Backend service for the Tutorly online tutoring marketplace platform. Built with FastAPI, SQLAlchemy, and PostgreSQL/SQLite.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (development) → PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT tokens with bcrypt
- **Payment**: Stripe & PayPal
- **Email**: SendGrid
- **File Storage**: AWS S3
- **Background Jobs**: Celery with Redis
- **Real-time**: WebSockets

## Project Structure

```
backend/
├── app/
│   ├── models/          # Database models (User, Instructor, Student, etc.)
│   ├── services/        # Business logic layer
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic schemas for validation
│   ├── database/        # Database configuration and connection
│   ├── core/            # Core settings, security, dependencies
│   ├── utils/           # Utility functions
│   ├── tasks/           # Celery background tasks
│   └── main.py          # FastAPI application entry point
├── tests/               # Test scripts
├── .env.dev             # Development environment variables
├── .env.prod            # Production environment variables
├── .env.example         # Environment template
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
├── alembic.ini          # Alembic configuration (to be created)
├── claude.md            # AI assistant development guide
├── prd.md               # Product Requirements Document
└── README.md            # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- pip or uv (for package management)
- Redis (for Celery and caching)
- PostgreSQL (for production)

### 2. Virtual Environment Setup

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using uv (recommended)
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env.dev

# Edit .env.dev with your configuration
# Update SECRET_KEY, database URL, API keys, etc.
```

### 5. Database Setup

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### 6. Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Or using Python
python app/main.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Development Workflow

### Running the Application

```bash
# Development mode (with auto-reload)
ENVIRONMENT=development uvicorn app.main:app --reload

# Production mode
ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check migration status
alembic current
alembic history
```

### Running Background Tasks (Celery)

```bash
# Start Celery worker
celery -A app.tasks worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.tasks beat --loglevel=info

# Or run both together
celery -A app.tasks worker --beat --loglevel=info
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## API Endpoints (Planned)

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout

### Instructor
- `POST /api/instructor/onboarding/*` - 7-step onboarding
- `GET /api/instructor/profile` - Get profile
- `PATCH /api/instructor/profile` - Update profile
- `GET /api/instructor/sessions` - Get upcoming sessions
- `GET /api/instructor/wallet` - Get wallet balance

### Student
- `GET /api/student/profile` - Get profile
- `PATCH /api/student/profile` - Update profile

### Search
- `GET /api/search/tutors` - Search tutors
- `GET /api/search/tutors/{id}` - Get tutor profile

### Booking
- `POST /api/booking/create` - Create booking
- `POST /api/booking/{id}/cancel` - Cancel booking

### Session
- `GET /api/session/{id}` - Get session details
- `POST /api/session/{id}/confirm` - Confirm session

### Messaging
- `GET /api/messaging/conversations` - Get conversations
- `POST /api/messaging/send` - Send message
- `WS /api/messaging/ws` - WebSocket connection

### Payment
- `POST /api/payment/create-intent` - Create payment
- `POST /api/payment/confirm` - Confirm payment

### Admin
- `GET /api/admin/verification/pending` - Pending verifications
- `POST /api/admin/verification/{id}/approve` - Approve profile

## Environment Variables

See `.env.example` for all required environment variables.

### Key Variables:
- `ENVIRONMENT`: `development` or `production`
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `STRIPE_SECRET_KEY`: Stripe API key
- `SENDGRID_API_KEY`: SendGrid API key
- `AWS_ACCESS_KEY_ID`: AWS S3 credentials
- `REDIS_URL`: Redis connection string

## Architecture Guidelines

### Service Layer Pattern
- All business logic in `app/services/`
- Routers are thin, only handle HTTP concerns
- Services handle validation, business rules, database operations

### Models in One Location
- All SQLAlchemy models in `app/models/`
- Never create models outside this directory
- Import models via `app/models/__init__.py`

### Database Migrations
- **Always** use Alembic for schema changes
- Never modify database directly
- Test migrations before applying to production

### Error Handling
1. Root Cause Analysis (RCA)
2. Fix Implementation
3. Test Script Creation
4. Iterative Testing
5. Cleanup (delete test scripts)

## Common Commands

```bash
# Format code with Black
black app/ tests/

# Lint with Ruff
ruff check app/ tests/

# Type check with mypy
mypy app/

# Generate requirements.txt from pyproject.toml
pip freeze > requirements.txt
```

## Production Deployment

### Database Migration

```bash
# Switch to PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/tutorly_db alembic upgrade head
```

### Environment Variables

- Update `.env.prod` with production values
- Use strong `SECRET_KEY`
- Configure production database URL
- Set `DEBUG=false`
- Configure proper `ALLOWED_ORIGINS`

### Running Production Server

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Documentation

- **Product Requirements**: See `prd.md`
- **Development Guide**: See `claude.md`
- **API Documentation**: http://localhost:8000/api/docs (when running)

## Support

For issues or questions, contact: dev-support@tutorlyplatform.com

---

**Version**: 0.1.0
**Last Updated**: 2025-11-04
