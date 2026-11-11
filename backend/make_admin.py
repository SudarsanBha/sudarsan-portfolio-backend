from getpass import getpass
from sqlalchemy import select
from app.database import SessionLocal
from app.models.users import User

def main():
    email = input("Enter the registered user's email: ").strip().lower()

    confirm = input(f"Promote {email} to admin? Type YES to confirm: ")

    if confirm != "YES":
        print("Cancelled.")
        return

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email)
        )

        if user is None:
            print("User not found.")
            return

        user.role = "admin"
        db.commit()

        print(f"Success: {user.email} now has role '{user.role}'.")

if __name__ == "__main__":
            main()