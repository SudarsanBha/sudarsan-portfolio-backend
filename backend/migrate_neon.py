import os
import getpass

from alembic import command
from alembic.config import Config

def main():
    print("Neon PostgreSQL migration")

    print("----------------")

    url = getpass.getpass("Paste your Neon pooled connection string (input hidden): ").strip()

    if url.startswith("postgresql://"):
        url = url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    if not url.startswith("postgresql+psycopg://"):
        raise SystemExit("Invalid PostgreSQL connection URL.")

    os.environ["DATABASE_URL"] = url

    print("\nStarting Alembic migration....")

    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")

    print("\nMigration completed Successfully.")



if __name__ == "__main__":
    main()