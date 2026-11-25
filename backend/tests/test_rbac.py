from datetime import datetime, timezone, timedelta

import jwt
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, get_db
from app.main import app
from app.models.users import User
from app.security import hash_password, create_access_token
from app.models.projects import Project as ProjectModel
from app.models.contact import ContactMessage as ContactMessageModel
from app.config import settings

# Isolate in-memory database for RBAC tests.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit = False
)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session


    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def create_test_user(db_session, email: str, role: str = "user", is_active: bool = True) -> User:
    user = User(
        full_name="Test User",
        email=email,
        hashed_password=hash_password("TestPassword123"),
        role=role,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def token_for(user: User) -> str:
    return create_access_token(
        subject=str(user.id),
        role=user.role,
    )


def test_admin_can_access_dashboard(client, db_session):
    admin=create_test_user(
        db_session,
        "admin-test@example.com",
        role="admin",
    )

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token_for(admin)}"},
    )

    assert response.status_code == 200
    assert response.json()["role"] =="admin"


def test_regular_user_cannot_access_dash(client, db_session):
    user=create_test_user(
        db_session,
        "user-test@example.com",
        role="user",
        )
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token_for(user)}"},
        )
    assert response.status_code == 403


def test_missing_token_cannot_access_dashboard(client):
    response = client.get("/api/admin/dashboard")

    assert response.status_code ==401


def test_inactive_user_with_valid_token_is_rejected(client, db_session):
    user=create_test_user(
        db_session,
        "inactive-test@example.com",
        role="admin",
        is_active=False,
    )
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token_for(user)}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] =="User account is inactive"


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer invalid.token.value"},
    )
    assert response.status_code == 401


def create_test_project(db_session) -> ProjectModel:
    project = ProjectModel(
        title= "Test Portofolio Project",
        description="A test project used to verify project permisiions",
        technologies=["Python", "FastAPI"]
    )

    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


def test_admin_can_create_project(client, db_session):
    admin = create_test_user(
        db_session,
        "project-admin@example.com",
        role="admin"
    )

    response = client.post(
        "/api/projects/",
        headers={"Authorization": f"Bearer {token_for(admin)}"},
        json={
            "title": "New Backend Project",
            "description": "A backend project created by an administrator.",
            "technologies": ["Python", "FastAPI", "SQLite"],
        },
    )

    assert response.status_code ==201
    assert response.json()["id"] is not None
    assert response.json()["title"] == "New Backend Project"


def test_regular_user_cannot_create_project(client, db_session):
    user = create_test_user(
        db_session,
        "project-user@example.com",
        role="user"
    )

    response = client.post(
        "/api/projects/",
        headers={"Authorization": f"Bearer {token_for(user)}"},
        json={
            "title": "Unauthorized Project",
            "description": "Post cannot be created by a user.",
            "technologies": ["Python", "FastAPI", "SQLite"],
        },
    )

    assert response.status_code == 403


def test_admin_can_update_project(client, db_session):
    admin = create_test_user(
        db_session,
        "update-admin@example.com",
        role="admin"
    )

    project = create_test_project(db_session)

    response = client.put(
        f"/api/projects/{project.id}",
        headers={"Authorization": f"Bearer {token_for(admin)}"},
        json= {
            "title": "Updated Backend Project",
            "description": "The project has been updated by an administrator.",
            "technologies": ["Python", "FastAPI", "PostgreSQL", "JS"]
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Backend Project"
    assert response.json()["technologies"] == ["Python", "FastAPI", "PostgreSQL", "JS"]


def test_admin_can_delete_project(client, db_session):
    admin = create_test_user(
        db_session,
        "delete-admin@example.com",
        role="admin"
    )

    project = create_test_project(db_session)

    project_id = project.id

    response = client.delete(
        f"/api/projects/{project_id}",
        headers = {"Authorization": f"Bearer {token_for(admin)}"},
    )

    assert response.status_code == 204
    assert db_session.get(ProjectModel, project_id) is None


def test_regular_user_cannot_update_or_delete_project(client, db_session):
    user = create_test_user(
        db_session,
        "restricted-user@example.com",
        role="user"
    )

    project = create_test_project(db_session)


    update_response = client.put(
        f"/api/projects/{project.id}",
        headers = {"Authorization": f"Bearer {token_for(user)}"},
        json={
            "title": "Unauthorized Update",
            "description": "A regular user can not change this project.",
            "technologies": ["Python"],
        },
    )

    delete_response = client.delete(
        f"/api/projects/{project.id}",
        headers = {"Authorization": f"Bearer {token_for(user)}"}
    )

    assert update_response.status_code == 403
    # print("UPDATE:", update_response.status_code,
    #      update_response.json())

    assert delete_response.status_code == 403
    #print("DELETE:",
    #      delete_response.status_code,
    #     delete_response.json())

    # Verify that original project still exists and was not changed

    db_session.refresh(project)
    assert project.title == "Test Portofolio Project"
    assert db_session.get(ProjectModel, project.id) is not None


def test_current_user_response_does_not_expose_password_hash(client, db_session):
    user = create_test_user(
        db_session,
        "privacy-test@example.com",
        role="user",
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token_for(user)}"},
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "hashed_password" not in response_data
    assert "password" not in response_data
    assert response_data["email"] == "privacy-test@example.com"


def test_public_user_cannot_assign_admin_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Registration Test",
            "email": "role-escalation@example.com",
            "password": "SecureTestPass123",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"


def test_contact_message_is_saved_to_database(client, db_session):
    response = client.post(
        "/api/contact/",
        json={
            "name": "Persistence Test",
            "email": "persistence@example.com",
            "message": "Please verify that this message is stored"
        },
    )
#print(response.json())

    assert response.status_code == 201
    assert response.json()["success"] is True

    saved_message = db_session.query(ContactMessageModel).filter_by(email="persistence@example.com").first()

    assert saved_message is not None
    assert saved_message.name == "Persistence Test"
    assert saved_message.message == (
        "Please verify that this message is stored"
    )
    assert saved_message.created_at is not None


def test_contact_database_failure_returns_500_and_rolls_back(
        client,
        db_session,
        monkeypatch):
    def fail_commit():
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(db_session, "commit", fail_commit)

    response = client.post(
        "/api/contact/",
        json={
            "name": "Failure Test",
            "email": "failure@example.com",
            "message": "lease test database failure handeling.",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to save contact message. "
    "Please try again.")
    saved_message = (db_session.query(ContactMessageModel)).filter_by(email="failure@example.com").first()
    assert saved_message is None


def test_admin_can_read_contact_messages(client, db_session):
    admin = create_test_user(
        db_session,
        "contact-admin@example.com",
        role="admin",
    )

    client.post(
        "/api/contact/",
        json={
            "name": "Private Contact",
            "email": "private-contact@example.com",
            "message": "This message should be visible to admins."
        },
    )

    response = client.get(
        "/api/admin/contact-messages/",
        headers = {"Authorization": f"Bearer {token_for(admin)}"},
    )

    assert response.status_code == 200

    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["email"] == "private-contact@example.com"
    assert messages[0]["name"] == "Private Contact"
    assert "created_at" in messages[0]


def test_regular_user_cannot_read_messages(client, db_session):
    user = create_test_user(
        db_session,
        "contact-user@example.com",
        role="user"
    )

    response = client.get(
        "/api/admin/contact-messages/",
        headers = {"Authorization": f"Bearer {token_for(user)}"}
    )

    assert response.status_code == 403


def test_unauthorized_user_cannot_read_messages(client):
    response = client.get("/api/admin/contact-messages/")

    assert response.status_code == 401


def test_admin_gets_empty_list_when_no_contact_messages(client, db_session):
    admin = create_test_user(
        db_session,
        "empty-contact-admin@example.com",
        role="admin"
    )

    response = client.get(
        "/api/admin/contact-messages",
        headers={
            "Authorization": f"Bearer {token_for(admin)}",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_expired_access_token_is_rejected(client, db_session):
    user = create_test_user(
        db_session,
        "expired-access@example.com",
        role="user",
    )

    expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)

    expired_token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
            "iat": expired_time - timedelta(minutes=5),
            "exp": expired_time,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_tampered_access_token_is_rejected(client, db_session):
    user = create_test_user(
        db_session,
        "tampered-token@example.com",
        role="user",
    )

    valid_token = token_for(user)

    header, payload, signature = valid_token.split(".")

    tampered_payload = payload[:-1] + (
        "A" if payload[0] != "A"
        else "B"
    )

    tampered_token = f"{header}.{tampered_payload}.{signature}"

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_unexpected_jwt_algorithm_is_rejected(client, db_session):
    user = create_test_user(
        db_session,
        "unexpected-algorithm@example.com",
        role="user",
    )

    unexpected_token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        settings.jwt_secret_key,
        algorithm="HS384",
    )

    response = client.get(
        "/api/auth/me",
        headers={"authorization": f"Bearer {unexpected_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"