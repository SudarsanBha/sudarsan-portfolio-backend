Sudarsan Portfolio — Full-Stack Developer Portfolio

A full-stack developer portfolio featuring a Python FastAPI backend and a responsive frontend built with HTML, CSS and JavaScript.

The backend provides authentication, role-based access control (RBAC), project management, contact-message handling, database migrations and administrator functionality.

The application is deployed using GitHub Pages, Render and Neon PostgreSQL.

Live Application

Service| Link
Portfolio website| "Visit Portfolio" (https://sudarsanbha.github.io/sudarsan-portfolio-backend/)
Backend API| "FastAPI Backend" (https://sudarsan-portfolio-backend.onrender.com/)
API Documentation| "Swagger UI" (https://sudarsan-portfolio-backend.onrender.com/docs)
ReDoc| "API Reference" (https://sudarsan-portfolio-backend.onrender.com/redoc)
Health Check| "API Health" (https://sudarsan-portfolio-backend.onrender.com/api/health)
GitHub Repository| "Source Code" (https://github.com/SudarsanBha/sudarsan-portfolio-backend)
Docker Hub| "Public Docker Image" (https://hub.docker.com/r/sudarsan4116/sudarsan-portfolio-api)

Project Overview

This project demonstrates practical backend development skills through a deployed portfolio application.

It includes:

- RESTful API development using FastAPI.
- JWT-based authentication.
- Password hashing with Argon2.
- Role-based access control.
- SQLAlchemy database integration.
- PostgreSQL production database.
- Alembic database migrations.
- Automated API testing.
- Docker containerization.
- Frontend-to-backend integration.
- Production deployment and environment configuration.

Features Implemented

Backend Development

- Authentication: User registration and login.
- JWT security: Token-based authentication.
- Password security: Argon2 password hashing.
- Role-based access control: Protected administrator endpoints.
- Project management: Public project listing and administrator CRUD operations.
- Contact management: Receive and store visitor messages.
- Admin dashboard: Protected administrator dashboard.
- Health monitoring: API health-check endpoint.
- Error handling: Structured API error responses.
- Configuration: Environment-based application settings.

Database

- SQLAlchemy 2.x ORM.
- SQLite for local development.
- Neon PostgreSQL for production.
- Alembic database migrations.
- Database schema versioning.
- Database integrity and migration checks.

Frontend

- Responsive HTML, CSS and JavaScript.
- Portfolio sections for About, Skills, Projects, Education and Contact.
- Contact form integrated with the production API.
- Successful end-to-end contact-message submission.

Testing and Quality

- Pytest automated test suite.
- HTTPX API testing.
- Authentication and authorization testing.
- Production endpoint verification.
- Database migration verification.

Latest verified test result: 27 passed.

Technology Stack

Area| Technologies
Backend| Python 3.12, FastAPI
Database| SQLite, PostgreSQL
ORM| SQLAlchemy 2.x
Database migrations| Alembic
Validation| Pydantic
Configuration| Pydantic Settings
Authentication| JWT
Password hashing| Argon2
Testing| Pytest, HTTPX
Frontend| HTML5, CSS3, JavaScript
Containerization| Docker, Docker Compose
Image registry| Docker Hub
Backend hosting| Render
Database hosting| Neon PostgreSQL
Frontend hosting| GitHub Pages
CI/CD| GitHub Actions
API documentation| Swagger UI, ReDoc

Application Architecture

                 VISITOR
                    |
                    v
          GitHub Pages Frontend
              HTML / CSS / JS
                    |
                    | HTTPS / REST API
                    v
             Render Platform
              FastAPI Backend
                    |
          +---------+----------+
          | | |
          v v v
       Auth Projects Contact
       Routes Routes Routes
          | | |
          +---------+----------+
                    |
                    v
             SQLAlchemy ORM
                    |
                    v
            Neon PostgreSQL
              Production DB

Local development uses SQLite, while the deployed application uses Neon PostgreSQL.

Project Structure

backend-portofolio/
│
├── backend/
│ ├── app/
│ │ ├── models/
│ │ ├── routes/
│ │ ├── schemas/
│ │ ├── config.py
│ │ ├── database.py
│ │ ├── dependencies.py
│ │ ├── main.py
│ │ └── security.py
│ │
│ ├── alembic/
│ ├── tests/
│ ├── Dockerfile
│ ├── requirements.txt
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
├── .gitignore
├── docker-compose.yml
└── README.md

Running Locally

Prerequisites

- Python 3.12+
- Git
- PowerShell (Windows)
- Docker Desktop (optional)

1. Clone the repository

git clone https://github.com/SudarsanBha/sudarsan-portfolio-backend.git

cd sudarsan-portfolio-backend

2. Set up the backend

cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

3. Configure environment variables

Create a local environment file:

Copy-Item .env.example .env

Configure your private values in ".env".

Example configuration:

ENVIRONMENT=development
DEBUG=true
FRONTEND_ORIGIN=http://localhost:5500

DATABASE_URL=sqlite:///./portofolio.db

JWT_SECRET_KEY=your-private-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Generate a strong, random JWT secret for local use. Never commit ".env" or expose your production secrets.

4. Run database migrations

alembic upgrade head

5. Start the backend

uvicorn app.main:app --reload

The backend will be available at:

- API: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/api/health

6. Start the frontend

Open a second PowerShell terminal in the project root:

python -m http.server 5500

Visit:

http://127.0.0.1:5500/frontend/

Docker

The project includes a Dockerfile and Docker Compose configuration.

The backend Docker image is also published publicly on Docker Hub:

Docker Hub: https://hub.docker.com/r/sudarsan4116/sudarsan-portfolio-api

Image:

sudarsan4116/sudarsan-portfolio-api:latest

Prerequisites

- Docker Desktop installed and running.
- A configured "backend/.env" file.
- An initialized local SQLite database at "backend/portofolio.db".

The database must exist before starting Docker Compose because the configuration uses a bind mount with automatic host-file creation disabled. Running the local Alembic migrations described above initializes the database.

Build the Docker image

Run these commands from the project root:

docker compose build backend

Start the backend container

docker compose up -d backend

Check container status

docker compose ps

View backend logs

docker compose logs -f backend

Verify the application

- API health: http://localhost:8000/api/health
- Projects endpoint: http://localhost:8000/api/projects/
- Swagger documentation: http://localhost:8000/docs

Stop the container

docker compose down

Docker configuration notes

- Docker Compose uses SQLite for local container testing.
- The local database is mounted from "backend/portofolio.db" into "/app/portofolio.db".
- The container uses the "appuser" non-root Linux user.
- The Docker image does not contain the local ".env" file or SQLite database.
- Environment variables are supplied at container runtime.
- The container includes a health check using "/api/health".
- Render production deployment uses Neon PostgreSQL rather than the local Docker SQLite database.

The Docker Compose configuration builds the image locally. The separately published Docker Hub image can also be pulled using:

docker pull sudarsan4116/sudarsan-portfolio-api:latest

Database Migrations

Alembic is used to manage database schema changes.

Run migrations:

alembic upgrade head

Check the current migration:

alembic current

View migration history:

alembic history

Check for model/schema differences:

alembic check

Running Tests

From the backend directory:

python -m pytest -q

The automated tests cover application functionality, API endpoints, authentication and role-based authorization.

Main API Endpoints

Method| Endpoint| Description| Access
GET| "/"| API welcome message| Public
GET| "/api/health"| Health check| Public
POST| "/api/auth/register"| Register a user| Public
POST| "/api/auth/login"| Authenticate a user| Public
GET| "/api/auth/me"| Get authenticated user| Authenticated
GET| "/api/projects/"| List projects| Public
GET| "/api/projects/{project_id}"| Get individual project| Public
POST| "/api/projects/"| Create project| Admin
PUT| "/api/projects/{project_id}"| Update project| Admin
DELETE| "/api/projects/{project_id}"| Delete project| Admin
POST| "/api/contact/"| Submit contact message| Public
GET| "/api/admin/dashboard"| Administrator dashboard| Admin
GET| "/api/admin/contact-messages"| Retrieve contact messages| Admin

Administrator endpoints require an authenticated user with the administrator role.

For request and response schemas, visit the live Swagger documentation.

Security

Security measures currently implemented include:

- Argon2 password hashing.
- JWT-based authentication.
- Role-based authorization.
- Protected administrator routes.
- Environment-based secret management.
- CORS configuration for the deployed frontend.
- Non-root Docker container user.
- Local environment files excluded from version control.
- Production database configuration.
- Database migration management.

Production secrets are configured through the hosting environment rather than committed to the repository.

Deployment

The application uses three primary deployment services:

Component| Platform
Frontend| GitHub Pages
Backend API| Render
Production database| Neon PostgreSQL

Deployment workflow

1. Code is committed and pushed to the GitHub "main" branch.
2. GitHub Actions builds and deploys the frontend to GitHub Pages.
3. Render deploys the FastAPI backend from the repository.
4. The backend connects to Neon PostgreSQL.
5. Alembic migrations manage production database schema changes.

The Docker image is separately published to Docker Hub for distribution and container testing.

Development Roadmap

The following features are planned for future development. They are not yet claimed as implemented.

1. Authentication and Security Enhancements

- Refresh-token authentication.
- Secure refresh-token rotation.
- Refresh-token revocation and logout.
- Token expiration and session management.
- Rate limiting for authentication endpoints.
- Brute-force protection.
- Improved request validation.
- Security audit logging.

2. Backend Performance and Data Management

- Pagination for project and message endpoints.
- Sorting by date, title and other fields.
- Filtering by project category, technology and status.
- Search functionality.
- Database indexing for frequently queried columns.
- Query optimization.
- Efficient database connection pooling.
- Improved asynchronous request processing.
- Background tasks for non-blocking operations.

3. Advanced API Features

- Advanced search and filtering combinations.
- Reusable pagination dependencies.
- Consistent response metadata.
- API versioning.
- Improved API error handling.
- Caching frequently requested data.
- Performance monitoring and logging.

4. Frontend Performance Enhancements

- Infinite scrolling for project listings.
- Lazy loading of images and other media.
- Optimized asset delivery.
- Improved loading states.
- Debounced search input.
- Dynamic project loading from the backend.
- Better frontend error handling.
- Responsive performance improvements.

5. Advanced Backend Architecture

- More extensive asynchronous database operations where beneficial.
- Redis caching.
- Background job processing.
- Structured logging and monitoring.
- Improved integration and performance tests.
- CI/CD quality gates and automated deployment checks.

6. Infrastructure and Production Readiness

- Automated database backup strategy.
- Improved production monitoring.
- Application performance monitoring.
- More comprehensive security testing.
- Docker deployment optimization.
- Automated test execution during CI/CD.
- Production reliability improvements.

Project Status

Current status: Deployed and operational.

The portfolio currently has a working frontend, production FastAPI backend, Neon PostgreSQL database, authentication, administrator authorization, database migrations, automated tests and end-to-end contact-message functionality.

Docker containerization has been verified locally, and the Docker image has been published publicly on Docker Hub.

Further security, performance and scalability improvements are planned as part of the project's ongoing development.

Author

Sudarsan Bhandari

Python Backend Developer | FastAPI | REST APIs | SQL | PostgreSQL

- Portfolio: https://sudarsanbha.github.io/sudarsan-portfolio-backend/
- GitHub: https://github.com/SudarsanBha

---

Built to demonstrate practical Python backend development, API design, database management, authentication, testing and deployment skills.
