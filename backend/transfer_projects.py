import getpass

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.projects import Project

def main():
    print("SQLite to Neon project transfer")

    print("---------------")

    neon_url = getpass.getpass(
        "Paste your Neon pooled connection string (input hidden): "
    ).strip()

    if neon_url.startswith("postgresql://"):
        neon_url = neon_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    if not neon_url.startswith("postgresql+psycopg://"):
        raise SystemExit("Invalid PostgreSQL connection URL.")

    target_engine = create_engine(
        neon_url,
        pool_pre_ping=True,
    )

    try:
        # Read projects from the local SQLite Database.
        with SessionLocal() as source_db:
            projects = source_db.scalars(select(Project).order_by(Project.id)).all()

            if len(projects) != 6:
                raise SystemExit(
                    f"Expected 6 local projects, found {len(projects)}. "
                    "Transfer stopped."
                )

            project_data = [
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "technologies": project.technologies,
                }
                for project in projects
            ]

        # Transfer Projects to Neon PostgreSQL
        with Session(target_engine) as target_db:
            added = 0
            updated = 0
            skipped = 0

            for data in project_data:
                existing = target_db.get(Project, data["id"])

                if existing is None:
                    target_db.add(Project(**data))
                    added += 1

                elif(
                    existing.title == data["title"] and
                    existing.description == data["description"] and
                    existing.technologies == data["technologies"]
                    ):
                    skipped += 1

                else:
                    existing.title = data["title"]
                    existing.description = data["description"]
                    existing.technologies = data["technologies"]
                    updated +=1

                    '''raise RuntimeError(
                        f"Neon already contains project ID {data['id']} "
                        "with different data. No overwrite performed."
                    )'''

            target_db.commit()

            total = len(target_db.scalars(select(Project)).all())

        print(f"Projects added: {added}")
        print(f"Identical projects skipped: {skipped}")
        print(f"Projects updated: {updated}")
        print(f"Total projects in Neon: {total}")

        if total != 6:
            raise RuntimeError(
                f"Expected 6 projects in Neon, found {total}."
            )

        print("Project transfer completed successfully.")

    finally:
        target_engine.dispose()


if __name__ == "__main__":
    main()