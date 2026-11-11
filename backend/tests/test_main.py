from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_existing_project():
    response = client.get("/api/projects/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_missing_projects():
    response = client.get("/api/projects/999")
    assert response.status_code == 404


def test_contact_valid_data():
    response = client.post(
        "/api/contact",
        json={
            "name": "Sudarsan Bhandari",
            "email": "sudarsan@email.com",
            "message": "Hello, this is a test message."
        },
    )
    assert response.status_code == 201
    assert response.json()["success"] is True


def test_contact_invalid_email():
    response = client.post(
        "/api/contact/",
        json={
            "name": "Sudarsan Bhandari",
            "email": "not-an-email",
            "message": "This is a test message"
        },
    )
    assert response.status_code == 422


def test_contact_rejects_whitespace_only_name():
    response = client.post(
        "/api/contact/",
        json = {
            "name": "    ",
            "email": "valid@example.com",
            "message": "This is a valid test message"
        }
    )

    assert response.status_code == 422


def test_contact_rejects_hitespace_only_message():
    response = client.post(
        "api/contact/",
        json = {
            "name": "Test user",
            "email": "valid@example.com",
            "message": "               ",
        },
    )

    assert response.status_code == 422