# Notes API

A production-ready REST API for managing notes with user authentication, built with FastAPI, SQLAlchemy, PostgreSQL, and JWT authentication. Fully Dockerized and deployable to AWS ECS Fargate.

## Features

- 🔐 **JWT Authentication** - Secure user registration and login
- 📝 **Notes CRUD** - Create, read, update, delete notes
- 👤 **User Isolation** - Each user can only access their own notes
- 🐳 **Fully Dockerized** - Backend and database run in Docker containers
- ☁️ **Cloud Deployable** - Deploy Docker containers to AWS ECS Fargate
- ✅ **Comprehensive Tests** - 20 test cases covering all functionality

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Production database
- **JWT (python-jose)** - Token-based authentication
- **Passlib + Bcrypt** - Password hashing
- **Pytest** - Testing framework
- **Docker** - Containerization

## Quick Start

```bash
# Start both backend and PostgreSQL
docker-compose up -d

# View logs (both services)
docker-compose logs -f

# Access the API
open http://localhost:8000/docs
```

## API Usage

### 1. Register & Login

Go to http://localhost:8000/docs (Swagger UI):

1. **POST /auth/register** → Register a user
2. **POST /auth/login** → Get your JWT token
3. Click **🔓 Authorize** → Paste your token
4. Now you can use all the notes endpoints!

### 2. API Endpoints

**Authentication (Public)**
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

**Notes (Protected - Requires JWT)**
- `POST /notes/` - Create a note
- `GET /notes/` - List all your notes
- `GET /notes/{id}` - Get a note by ID
- `PUT /notes/{id}` - Update a note
- `DELETE /notes/{id}` - Delete a note

**Health**
- `GET /health` - Health check

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests (uses in-memory SQLite)
python -m pytest tests/ -v
```

All 20 tests should pass! ✅

## Configuration

Configure via environment variables or `.env` file:

```bash
DATABASE_URL="postgresql://postgres:postgres@postgres:5432/notes"
SECRET_KEY="your-secret-key-here"  # Generate with: openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Deployment to AWS ECS

**Architecture:**
- **Backend**: ECS Fargate (Docker container)
- **Database**: RDS PostgreSQL (managed service, not a container)
- **Image Registry**: ECR

**Deployment Steps:**

1. **Create RDS PostgreSQL database** and note the connection endpoint
2. **Build and push Docker image to ECR**
   ```bash
   docker build -t notes-api .
   docker tag notes-api:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/notes-api:latest
   docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/notes-api:latest
   ```
3. **Create ECS cluster** (Fargate) and task definition using your ECR image
4. **Set environment variables** in task definition:
   - `DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/notes`
   - `SECRET_KEY=your-secure-key-here`
5. **Configure security groups** (ECS → RDS on port 5432, Internet → ECS on port 8000)
6. **Deploy ECS service** with desired task count

**Note:** Local dev uses `docker-compose` (both backend + database containers). AWS production uses ECS + RDS (backend container + managed database).

## Project Structure

```
notes-api/
├── app/
│   ├── main.py          # FastAPI application
│   ├── api/v1/
│   │   ├── auth.py      # Authentication endpoints
│   │   └── notes.py     # Notes endpoints
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── crud/            # Database operations
│   └── core/
│       ├── config.py    # Settings
│       ├── db.py        # Database config
│       └── security.py  # JWT & password hashing
├── tests/
│   └── test_notes.py    # API tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Security Notes

- Passwords are hashed with bcrypt
- JWT tokens expire after 30 minutes (configurable)
- All note endpoints require authentication
- Users can only access their own notes
- **⚠️ IMPORTANT**: The default `SECRET_KEY` in `config.py` is for demo/development only. For production deployments, generate a secure key using `openssl rand -hex 32` and set it as an environment variable

## License

MIT License - Feel free to use this project for learning and development!
