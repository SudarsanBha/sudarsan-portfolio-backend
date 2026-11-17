from sqlalchemy import select
from app.database import SessionLocal
from app.models.projects import Project

INITIAL_PROJECTS = [
    {
        "id": 1,
        "title": "Real-Time  Messaging Platform",
        "description": "Real-Time chat application built with FastAPI, and WebSockets, enablig instant communication between users through ersistent connections.",
        "technologies": ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
    },
    {
        "id": 2,
        "title": "Travel Booking System",
        "description": "A secure Travel Booking System built with Python, FastAPI, PostgreSQL, featuring flight and hotel reservations, user authentication, role-based access control (RBAC), and payment integration.",
        "technologies": ["Python", "FastAPI", "PostgreSQL", "Alembic", "JWT", "RBAC", "Rest API", "Payment Integration", "SQLAlchemy"],
    },
    {
        "id": 3,
        "title": "Digital Bus Card Using QR Code",
        "description": "A Digital Bus Card System built with Python, FastAPI, and PostgreSQL, enabling users to manage digital bus cards, generate QR-code tickets, and validate journeys through secure QR-code scanning.",
        "technologies": ["Python", "FastAPI", "QR Code", "PostgreSQL", "JWT", "RBAC", "Alembic", "Rest API", "Payment Integration"],
    },
    {
        "id": 4,
        "title": "Job Tracking System",
        "description": "A FastAPI backend for managing job applications, featuring RESTful API database integration, structured application architecture.",
        "technologies": ["Python", "FastAPI", "SQLite"],
    },
    {
        "id": 5,
        "title": "User Authentication Application",
        "description": "A FastAPI backend featuring JWT, authentication and authorization, SQLAlchemy database integration, and a notes management system with full CRUD operations.",
        "technologies": ["Python", "FastAPI", "SQLAlchemy", "SQLite", "Pydantic", "JWT"],
    },
    {
        "id": 6,
        "title": "To-Do Application",
        "description": "A beginner-friendly backend API built with FastAPI, featuring full CRUD functionality for task management using SQLite database.",
        "technologies": ["Python", "FastAPI", "SQLite"],
    },
]

def main():
    #Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        added = 0
        updated = 0

        for project_data in INITIAL_PROJECTS:
            project_id = project_data["id"]
            existing_project = db.get(Project, project_id)

            if existing_project is None:
                db.add(Project(**project_data))
                added +=1
            else:
                existing_project.title = project_data["title"]
                existing_project.description = project_data["description"]
                existing_project.technologies = project_data["technologies"]
                updated += 1

        db.commit()

        total = len(db.scalars(select(Project)).all())

        print(f"Projects added: {added}")
        print(f"Existing projects updated: {updated}")
        print(f"Total projects in database: {total}")

if __name__ =="__main__":
    main()