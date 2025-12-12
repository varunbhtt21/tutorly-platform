# Tutorly Platform Backend - Quick Start Guide

## Prerequisites

- Python 3.11+ (you have Python 3.14 ✓)
- pip or uv package manager

## Setup & Installation

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the Server

### Development Mode (with auto-reload)

```bash
# Activate virtual environment first
source venv/bin/activate

# Option 1: Using Python directly
python3 app/main.py

# Option 2: Using uvicorn
uvicorn app.main:app --reload --port 8000
```

The server will start at: **http://localhost:8000**

## Testing the API

### Option 1: Interactive API Documentation (Swagger UI)

Visit: **http://localhost:8000/api/docs**

This provides:
- Complete API documentation
- Try-it-out functionality for all endpoints
- Request/response schemas
- Authentication testing

### Option 2: Automated Test Script

```bash
# With server running in another terminal, run:
python3 tests/test_auth_flow.py
```

This will test:
- ✓ Server health check
- ✓ User registration (instructor & student)
- ✓ User login
- ✓ Protected endpoints
- ✓ Token refresh
- ✓ Security validation

### Option 3: Manual Testing with curl

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }'

# 2. Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# 3. Get current user (use access_token from login response)
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Available Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/docs` - Interactive API documentation
- `GET /api/redoc` - ReDoc documentation

### Authentication (All under `/api/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `POST /password-reset/request` - Request password reset
- `POST /password-reset/confirm` - Confirm password reset
- `POST /verify-email` - Verify email address
- `POST /change-password` - Change password (authenticated)
- `GET /me` - Get current user profile (authenticated)
- `POST /logout` - Logout (authenticated)

## Database

The application uses **SQLite** in development mode. The database file will be created automatically at:

```
tutorly_platform_dev.db
```

### Viewing the Database

You can use any SQLite browser:
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLite Viewer (VS Code Extension)](https://marketplace.visualstudio.com/items?itemName=alexcvzz.vscode-sqlite)

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Import Errors

Make sure you're in the virtual environment:

```bash
# Check if venv is activated (you should see (venv) in your prompt)
which python3

# If not activated:
source venv/bin/activate
```

### Database Errors

If you encounter database errors, delete the database file and restart:

```bash
rm tutorly_platform_dev.db
python3 app/main.py
```

## Environment Configuration

The application uses `.env.dev` for development settings. Key settings:

- `ENVIRONMENT=development`
- `DATABASE_URL=sqlite:///./tutorly_platform_dev.db`
- `SECRET_KEY=dev-secret-key-change-this-before-production-...`
- `DEBUG=true`
- `LOG_LEVEL=DEBUG`

**⚠️ IMPORTANT**: Never use the development SECRET_KEY in production!

## Next Steps

1. ✅ **Complete** - Authentication system is working
2. 🚧 **Next** - Implement Instructor Onboarding (7-step process)
3. ⏳ **Future** - File Upload, Search, Booking, Sessions, Messaging, Payments

## Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration, security, dependencies
│   ├── models/         # Database models (SQLAlchemy)
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic layer
│   ├── schemas/        # Pydantic schemas (DTOs)
│   ├── routers/        # API endpoints
│   └── main.py         # FastAPI application
├── tests/              # Test scripts
├── docs/               # Documentation
├── requirements.txt    # Python dependencies
├── .env.dev           # Development environment variables
└── setup.sh           # Setup script
```

## Documentation

- **PRD** - [prd.md](prd.md) - Product Requirements
- **Development Guide** - [claude.md](claude.md) - Development guidelines
- **Implementation Tracker** - [docs/v1_implementation.md](docs/v1_implementation.md) - Progress tracking
- **README** - [README.md](README.md) - Full documentation

## Support

For issues or questions:
- Check the [README.md](README.md)
- Review the [Implementation Tracker](docs/v1_implementation.md)
- Check API docs at http://localhost:8000/api/docs

---

**Happy coding! 🚀**
