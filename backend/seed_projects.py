from sqlalchemy import select
from app.database import Base, SessionLocal, engine
from app.models.projects import Project

INITIAL_PROJECTS = [
    {
        "id": 1,
        "title": "Real-Time  Messaging Platform",
        "description": "Real-Time chat application built with FastAI, and WebSockets.",
        "technologies": ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
    },

    {
        "id": 2,
        "title": "Real-Time  Messaging Platform",
        "description": "Real-Time chat application built with FastAI, and WebSockets.",
        "technologies": ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
    },

    {
        "id": 3,
        "title": "Real-Time  Messaging Platform",
        "description": "Real-Time chat application built with FastAI, and WebSockets.",
        "technologies": ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
    },

    {
        "id": 4,
        "title": "Real-Time  Messaging Platform",
        "description": "Real-Time chat application built with FastAI, and WebSockets.",
        "technologies": ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
    },
]


def main():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        added = 0
        skipped = 0

        for project_data in INITIAL_PROJECTS:
            existing_project = db.get(Project, project_data["id"])

            if existing_project is not None:
                skipped += 1
                continue

            db.add(Project(**project_data))
            added +=1

        db.commit()

        print(f"Projects(added: {added})")
        print(f"Existing projects skippped: {skipped}")
        print(f"Total projects in database: {len(db.scalars(select(Project)).all())}")

if __name__ =="__main__":
    main()