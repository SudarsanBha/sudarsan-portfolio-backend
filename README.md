Sudarsan Portfolio

A personal developer portfolio with a Python FastAPI backend and a responsive HTML, CSS, and JavaScript frontend. The backend provides authentication, role-based access control, project management, and contact-message handling.

Features

- Authentication: User registration, login, and JWT-based authentication.
- Password security: Argon2 password hashing.
- Role-based access control: Protected administrator endpoints.
- Project management: Public project listing and administrator CRUD operations.
- Contact form: Saves submitted messages to the database.
- Admin endpoints: Dashboard and contact-message management.
- Database migrations: Alembic.
- Automated tests: Pytest and HTTPX.
- Containerization: Docker and Docker Compose.
- API documentation: Interactive Swagger UI.

Technology Stack

Area| Technologies
Backend| Python 3.12, FastAPI
Database| SQLite, SQLAlchemy 2.x
Migrations| Alembic
Validation and configuration| Pydantic, Pydantic Settings
Authentication| JWT, Argon2
Testing| Pytest, HTTPX
Frontend| HTML, CSS, JavaScript
Deployment preparation| Docker, Docker Compose

Project Structure

backend-portofolio/
├── backend/
│ ├── alembic/
│ ├── app/
│ │ ├── models/
│ │ ├── routes/
│ │ ├── schemas/
│ │ ├── config.py
│ │ ├── database.py
│ │ ├── dependencies.py
│ │ ├── main.py
│ │ └── security.py
│ ├── tests/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── alembic.ini
├── frontend/
│ ├── css/
│ ├── js/
│ └── index.html
├── docker-compose.yml
├── .gitignore
└── README.md

Running Locally:

1. Start the backend

Open PowerShell in the project root:

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Create your local environment file from the example if you do not already have one:

Copy-Item .env.example .env

Configure the values in ".env", including a strong, private JWT secret. Never commit ".env" or share its secrets.

Run database migrations:

alembic upgrade head

Start the API:

uvicorn app.main:app --reload

The backend will be available at:

- API: http://127.0.0.1:8000
- Swagger documentation: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/api/health

2. Start the frontend

Open a second PowerShell terminal in the project root:

python -m http.server 5500

Open:

http://127.0.0.1:5500/frontend/

Running with Docker Compose

From the project root, build and start the backend container:

docker compose up -d --build

Check the container status:

docker compose ps

View backend logs:

docker compose logs -f backend

Stop the containers:

docker compose down

The SQLite database is stored locally at "backend/portofolio.db" and mounted into the backend container. It is excluded from Git.

Database Migrations

The project uses Alembic to manage database schema changes.

From the "backend" directory:

alembic upgrade head

Check the current migration:

alembic current

Check whether model changes require a new migration:

alembic check

Running Tests

From the "backend" directory:

python -m pytest -q

The test suite covers application endpoints and role-based access control.

Main API Endpoints

Method| Endpoint| Description
GET| "/"| API welcome message
GET| "/api/health"| Health check
POST| "/api/auth/register"| Register a user
POST| "/api/auth/login"| Authenticate a user
GET| "/api/auth/me"| Get the authenticated user
GET| "/api/projects"| List projects
GET| "/api/projects/{project_id}"| Get a project
POST| "/api/projects"| Create a project (admin)
PUT| "/api/projects/{project_id}"| Update a project (admin)
DELETE| "/api/projects/{project_id}"| Delete a project (admin)
POST| "/api/contact/"| Submit a contact message
GET| "/api/admin/dashboard"| Administrator dashboard
GET| "/api/admin/contact-messages"| List contact messages (admin)

Administrator endpoints require an authenticated user with the administrator role.

Security Notes

- Passwords are hashed using Argon2.
- JWT tokens are used for authentication.
- Administrator endpoints are protected by role-based authorization.
- Secrets and local environment files are excluded from version control.
- The application runs as a non-root user inside its Docker container.
- Database files and local development artifacts are excluded from Git.

Before deploying publicly, configure production environment variables, a secure database, HTTPS, and the appropriate frontend origin.

Project Status

The portfolio backend, frontend integration, authentication, database migrations, automated tests, and Docker configuration have been implemented.

The project is being prepared for deployment and further development.
