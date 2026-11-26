Sudarsan Portfolio — Full-Stack Developer Portfolio
A full-stack developer portfolio featuring a Python FastAPI backend and a responsive frontend built with HTML, CSS and JavaScript.

The backend demonstrates practical API development, authentication, role-based access control, refresh-token security, database management, automated testing, Docker containerization and cloud deployment.

Live application: Visit Portfolio

Live Application
Service Link
Portfolio website Visit Portfolio
Backend API FastAPI Backend
Swagger UI API Documentation
ReDoc API Reference
Health Check API Health
GitHub Repository Source Code
Docker Hub Public Docker Image
Project Overview
This project demonstrates practical backend development skills through a deployed portfolio application.

The application includes:

RESTful API development using FastAPI.
User registration and authentication.
JWT access-token and refresh-token authentication.
Secure refresh-token rotation and revocation.
Refresh-token reuse detection.
Role-based access control (RBAC).
Argon2 password hashing.
SQLAlchemy database integration.
PostgreSQL production database.
Alembic database migrations.
Automated API and security testing.
Docker containerization.
Frontend-to-backend integration.
Cloud deployment and environment-based configuration.
Features Implemented
Backend Development
User registration and login.
JWT access-token authentication.
Refresh-token authentication with rotation.
Refresh-token revocation and logout.
Refresh-token reuse detection and token-family revocation.
Role-based access control.
Protected administrator endpoints.
Public project listing and administrator project CRUD.
Contact-message submission and storage.
Administrator dashboard.
Health-check endpoint.
Environment-based application configuration.
Database error handling and transaction management.
Authentication and Security
Argon2 password hashing.
Separate secrets for access and refresh tokens.
Configurable access-token expiration.
Configurable refresh-token expiration.
Refresh tokens stored as SHA-256 hashes in the database.
Refresh-token rotation and revocation.
Refresh-token family tracking.
Detection of previously used refresh tokens.
JWT token-type validation.
JWT algorithm allow-list.
Database-backed user and role verification.
Inactive-account protection.
Protected administrator routes.
Database
SQLAlchemy 2.x ORM.
SQLite for local development.
Neon PostgreSQL for production.
Alembic database migrations.
Database schema versioning.
Database integrity and migration checks.
Persistent refresh-token records.
Frontend
Responsive HTML, CSS and JavaScript.
About, Skills, Projects, Education and Contact sections.
Contact form integrated with the backend API.
Production API integration.
Testing and Quality
Pytest automated test suite.
HTTPX API testing.
Authentication and authorization tests.
Refresh-token lifecycle tests.
JWT security tests.
Database and API error-handling tests.
Code coverage reporting.
Latest verified test result: 44 passed.

Total code coverage: 90%.

Technology Stack
Area Technologies
Language Python 3.12+
Backend framework FastAPI
Database SQLite, PostgreSQL
ORM SQLAlchemy 2.x
Database migrations Alembic
Data validation Pydantic
Configuration Pydantic Settings
Authentication PyJWT, JWT
Password hashing Argon2
Testing Pytest, HTTPX, pytest-cov
Frontend HTML5, CSS3, JavaScript
Containerization Docker, Docker Compose
Image registry Docker Hub
Backend hosting Render
Database hosting Neon PostgreSQL
Frontend hosting GitHub Pages
CI/CD GitHub Actions
API documentation Swagger UI, ReDoc
Application Architecture
VISITOR
|
v
GitHub Pages
HTML / CSS / JavaScript
|
| HTTPS / REST API
v
Render Platform
FastAPI Backend
|
+----------+----------+
| | |
v v v
Auth Projects Contact
Routes Routes Routes
| | |
+----------+----------+
|
v
SQLAlchemy ORM
|
v
Neon PostgreSQL
Production DB
Local development uses SQLite, while the deployed application uses Neon PostgreSQL.

The backend follows a modular monolithic architecture, separating routes, models, schemas, dependencies and business logic.

Project Structure
backend-portofolio/
│
├── backend/
│ ├── app/
│ │ ├── models/
│ │ │ ├── users.py
│ │ │ ├── projects.py
│ │ │ ├── contact.py
│ │ │ └── refresh_tokens.py
│ │ │
│ │ ├── routes/
│ │ │ ├── auth.py
│ │ │ ├── admin.py
│ │ │ ├── projects.py
│ │ │ └── contact.py
│ │ │
│ │ ├── schemas/
│ │ ├── services/
│ │ │ └── refresh_tokens.py
│ │ │
│ │ ├── config.py
│ │ ├── database.py
│ │ ├── dependencies.py
│ │ ├── main.py
│ │ └── security.py
│ │
│ ├── alembic/
│ │ └── versions/
│ ├── tests/
│ │ ├── test_main.py
│ │ ├── test_rbac.py
│ │ └── test_refresh_tokens.py
│ │
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── pytest.ini
│ └── alembic.ini
│
├── frontend/
│ ├── css/
│ ├── js/
│ └── index.html
│
├── .github/
│ └── workflows/
│
├── docker-compose.yml
└── README.md
Running Locally
Prerequisites
Python 3.12 or newer.
Git.
PowerShell (Windows).
Docker Desktop (optional).

1. Clone the repository
   git clone https://github.com/SudarsanBha/sudarsan-portfolio-backend.git

cd sudarsan-portfolio-backend 2. Set up the backend
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
Install the coverage dependency if it is not already included in the project dependencies:

python -m pip install pytest-cov 3. Configure environment variables
Create a local environment file:

Copy-Item .env.example .env
Configure your private values in .env.

Example configuration:

ENVIRONMENT=development
DEBUG=true

FRONTEND_ORIGIN=http://localhost:5500

DATABASE_URL=sqlite:///./portofolio.db

JWT_SECRET_KEY=your-access-token-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_SECRET_KEY=your-refresh-token-secret
REFRESH_TOKEN_EXPIRE_DAYS=7
Generate strong, random and separate secrets for access and refresh tokens.

Never commit .env or expose production credentials.

4. Run database migrations
   alembic upgrade head
5. Start the backend
   uvicorn app.main:app --reload
   The backend will be available at:

API: http://127.0.0.1:8000/
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
Health check: http://127.0.0.1:8000/api/health 6. Start the frontend
Open a second PowerShell terminal in the project root:

python -m http.server 5500
Visit:

http://127.0.0.1:5500/frontend/

Docker
The project includes a Dockerfile and Docker Compose configuration.

The backend image is also published publicly:

Docker Hub — sudarsan-portfolio-api

Image:

sudarsan4116/sudarsan-portfolio-api:latest
Prerequisites
Docker Desktop installed and running.
A configured backend/.env file.
An initialized local SQLite database at backend/portofolio.db.
Build the Docker image
Run from the project root:

docker compose build backend
Start the backend container
docker compose up -d backend
Check container status
docker compose ps
View backend logs
docker compose logs -f backend
Verify the application
Health: http://localhost:8000/api/health
Projects: http://localhost:8000/api/projects/
Swagger: http://localhost:8000/docs
Stop the container
docker compose down
Docker configuration
Docker Compose uses SQLite for local container testing.
The local database is mounted from backend/portofolio.db into /app/portofolio.db.
The container runs as a non-root Linux user named appuser.
The Docker image does not contain the local .env file or SQLite database.
Environment variables are supplied at container runtime.
The container includes a health check using /api/health.
Render production deployment uses Neon PostgreSQL rather than the local Docker SQLite database.
The Docker Compose configuration builds the image locally. The published Docker Hub image can also be pulled:

docker pull sudarsan4116/sudarsan-portfolio-api:latest
Database Migrations
Alembic manages database schema changes.

Run migrations:

alembic upgrade head
Check the current migration:

alembic current
View migration history:

alembic history
Check for model and schema differences:

alembic check
Running Tests
Run from the backend directory.

Execute the complete test suite:

python -m pytest
The project's pytest.ini automatically enables coverage reporting:

[pytest]
pythonpath = .
testpaths = tests
addopts = --cov=app --cov-report=term-missing
Run tests with a concise output:

python -m pytest -q
Run coverage with a detailed report:

python -m pytest --cov=app --cov-report=term-missing
Latest verified results
Metric Result
Total tests 44
Passed 44
Failed 0
Total statements 559
Missed statements 57
Overall coverage 90%
Coverage is measured across the app package. The results represent the latest verified test run and may change as the project develops.

Main API Endpoints
Method Endpoint Description Access
GET / API welcome message Public
GET /api/health Health check Public
POST /api/auth/register Register a user Public
POST /api/auth/login Authenticate a user Public
POST /api/auth/refresh Rotate refresh token and issue new tokens Refresh token
POST /api/auth/logout Revoke refresh token Refresh token
GET /api/auth/me Get authenticated user Authenticated
GET /api/projects/ List projects Public
GET /api/projects/{project_id} Get individual project Public
POST /api/projects/ Create project Admin
PUT /api/projects/{project_id} Update project Admin
DELETE /api/projects/{project_id} Delete project Admin
POST /api/contact/ Submit contact message Public
GET /api/admin/dashboard Administrator dashboard Admin
GET /api/admin/contact-messages Retrieve contact messages Admin
Administrator endpoints require an authenticated user with the administrator role.

For request and response schemas, visit the live Swagger documentation.

Security
Security measures currently implemented include:

Argon2 password hashing.
JWT-based authentication.
Separate access-token and refresh-token secrets.
Configurable token expiration.
JWT algorithm allow-list.
Access and refresh token-type validation.
Refresh-token hashes stored in the database.
Secure refresh-token rotation.
Refresh-token revocation and logout.
Refresh-token reuse detection and family revocation.
Database-backed user and role verification.
Inactive-account protection.
Role-based authorization.
Protected administrator routes.
Environment-based secret management.
CORS configuration.
Non-root Docker container user.
Local environment files excluded from version control.
Production database configuration.
Alembic database migration management.
Production secrets are configured through the hosting environment rather than committed to the repository.

Deployment
The application uses three primary deployment services:

Component Platform
Frontend GitHub Pages
Backend API Render
Production database Neon PostgreSQL
Deployment workflow
Code is committed and pushed to the GitHub main branch.
GitHub Actions builds and deploys the frontend to GitHub Pages.
Render deploys the FastAPI backend from the repository.
The backend connects to Neon PostgreSQL.
Alembic migrations manage production database schema changes.
The Docker image is separately published to Docker Hub for distribution and container testing.

Development Roadmap
The following items are planned improvements, not features currently claimed as implemented.

1. Authentication and Security Enhancements
   Rate limiting for authentication endpoints.
   Brute-force protection.
   Improved request validation.
   Security audit logging.
   Additional concurrency and failure-handling tests.
   Security response headers and CORS review.
2. Backend Performance and Data Management
   Pagination for project and message endpoints.
   Sorting and filtering.
   Search functionality.
   Database indexing for frequently queried columns.
   Query optimization and performance benchmarking.
   Review and optimize database connection pooling.
3. Advanced API Features
   Reusable pagination dependencies.
   Consistent response metadata.
   API versioning.
   Advanced search and filtering combinations.
   Background tasks where beneficial.
4. Frontend Performance Enhancements
   Dynamic project loading from the backend.
   Infinite scrolling.
   Lazy loading of images and media.
   Debounced search input.
   Improved loading and error states.
   Optimized asset delivery.
5. Caching and Architecture
   Redis caching.
   Cache invalidation and expiration strategies.
   Background job processing.
   Evaluate asynchronous database operations where beneficial.
   Structured logging and monitoring.
6. Infrastructure and Production Readiness
   Docker image optimization.
   Local PostgreSQL and Redis development environments.
   Kubernetes deployment and orchestration.
   Automated database backup strategy.
   Application performance monitoring.
   CI/CD quality gates.
   Improved integration and performance testing.
   Project Status
   Current status: Deployed and operational.

The portfolio currently has:

A working frontend hosted on GitHub Pages.
A production FastAPI backend hosted on Render.
A Neon PostgreSQL production database.
User authentication and role-based authorization.
Secure refresh-token rotation and revocation.
Administrator functionality.
Database migrations managed by Alembic.
Automated tests with 90% verified code coverage.
Docker containerization and a public Docker Hub image.
End-to-end contact-message functionality.
Further security, performance, scalability and infrastructure improvements are planned as part of the project's ongoing development.

Author
Sudarsan Bhandari

Python Backend Developer | FastAPI | REST APIs | SQL | PostgreSQL

Portfolio: https://sudarsanbha.github.io/sudarsan-portfolio-backend/
GitHub: https://github.com/SudarsanBha
Built to demonstrate practical Python backend development, API design, database management, authentication, testing, containerization and deployment skills.
