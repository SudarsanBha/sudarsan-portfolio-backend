from datetime import datetime, timezone, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.users import User
from app.models.refresh_tokens import RefreshToken
from app.security import hash_password, hash_refresh_token
from app.config import settings
from app.services.refresh_tokens import create_and_store_refresh_token


# Create an isolated in-memory SQLite database
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db=TestingSessionLocal()

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


def create_test_user(
    db_session,
    email="refresh-test@example.com",
    is_active=True
):
    user = User(
        full_name="Refresh Test User",
        email=email,
        hashed_password=hash_password("TestPassword123"),
        role="user",
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_login_creates_access_and_refresh_tokens(client, db_session):
    user = create_test_user(db_session)

    response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code== 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify that the refresh token is stored as a hash.
    refresh_record = (
        db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
    )

    assert refresh_record is not None
    assert refresh_record.token_hash != data["refresh_token"]


def test_refresh_token_rotation(client, db_session):
    user = create_test_user(db_session)

    # Login to obtain initial tokens.
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123",
        },
    )

    old_refresh_token = login_response.json()["refresh_token"]

    old_record = db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()

    old_family_id = old_record.family_id

    # Exchange the old refresh token for new tokens.
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert refresh_response.status_code == 200
    db_session.refresh(old_record)
    assert old_record.revoked_at is not None

    new_tokens = refresh_response.json()

    assert new_tokens["access_token"]
    assert new_tokens["refresh_token"]
    assert new_tokens["refresh_token"] != old_refresh_token

    # Verify the new token belongs to the same token family.
    new_record = (
        db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).filter(RefreshToken.id != old_record.id).first()
    )

    assert new_record is not None
    assert new_record.family_id == old_family_id
    assert new_record.revoked_at is None


def test_reusing_old_refresh_token_revokes_token_family(client, db_session):
    user = create_test_user(db_session)

    # First Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123",
        },
    )

    old_refresh_token = login_response.json()["refresh_token"]

    # Rotate the refresh token.
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert refresh_response.status_code == 200

    # new_refresh_token = refresh_response.json()["refresh_token"]

    # Attempt to reuse the old refresh token.
    reuse_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert reuse_response.status_code == 401

    # Verify that every token in the family has been revoked.
    token_records = (
        db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).all()
    )

    assert len(token_records) == 2

    for record in token_records:
        assert record.revoked_at is not None


def test_logout_revokes_refresh_token(client, db_session):
    user = create_test_user(db_session)

    # Login.
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123"
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    access_token = login_response.json()["access_token"]

    # Logout.
    logout_response = client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 204

    # Verify that the token has been revoked
    token_record = (
        db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
    )

    assert token_record is not None
    assert token_record.revoked_at is not None

    # Verify that revoked token can not be refreshed
    refresh_response = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert refresh_response.status_code == 401

    # Verify that the existing access token remains valid after logout.
    me_response=client.get(
        "/api/auth/me",
        headers={"Authorization": f"bearer {access_token}"},
    )

    assert me_response.status_code == 200


def test_invalid_token_is_rejected(client):
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": "this-is-not-a-valid-jwt",},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_inactive_user_cannot_refresh_token(client, db_session):
    
    user = create_test_user(db_session, is_active=True,)

    # Create refresh token while the user is still active user
    refresh_token = create_and_store_refresh_token(
        db=db_session,
        user_id = user.id,
    )

    db_session.commit()

    # Deactivate the user after the token has been issued
    user.is_active = False
    db_session.commit()

    # Attempt to refresh the token.
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401

    # Vaeify that the token family was revoked
    token_record = (
        db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
    )
    assert token_record is not None
    assert token_record.revoked_at is not None
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_expired_refresh_token_is_rejected(client, db_session):

    user = create_test_user(db_session)

    expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)

    expired_token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "type": "refresh",
            "jti": "expired-test-token",
            "iat": expired_time - timedelta(minutes=5),
            "exp": expired_time,
        },
        settings.refresh_token_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash = hash_refresh_token(expired_token),
        jti="expired-test-token",
        family_id="expired-test-family",
        expires_at=expired_time,
        )

    db_session.add(refresh_record)
    db_session.commit()

    response = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": expired_token
        },
    )

    assert response.status_code == 401


def test_refresh_token_with_empty_jti_is_rejected(client, db_session):
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "1",
            "role": "user",
            "type": "refresh",
            "jti": "",
            "iat": now,
            "exp": now + timedelta(days=7),
        },
        settings.refresh_token_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": token
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_refresh_token_with_empty_sub_is_rejected(client, db_session):
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "",
            "role": "user",
            "type": "refresh",
            "jti": "valid-test-jti",
            "iat": now,
            "exp": now + timedelta(days=7),
        },
        settings.refresh_token_secret_key,
        algorithm=settings.jwt_algorithm
    )

    response = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": token
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_access_token_cannot_be_used_as_refresh_token(client):
    now = datetime.now(timezone.utc)

    access_token = jwt.encode(
        {
            "sub": "1",
            "role": "user",
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.post(
        "api/auth/refresh",
        json={
            "refresh_token": access_token,
        },
    )

    assert response.status_code == 401


def test_logout_rejects_invalid_refresh_token(client):
    response = client.post(
        "/api/auth/logout",
        json={"refresh_token": "invalid.token.value"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_logout_rejects_expired_refresh_token(client, db_session):
    user = create_test_user(db_session)

    now = datetime.now(timezone.utc)
    jti = "expired-logout-test"

    expired_token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "type": "refresh",
            "jti": jti,
            "iat": now - timedelta(days=2),
            "exp": now - timedelta(days=1),
        },
        settings.refresh_token_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(expired_token),
        jti=jti,
        family_id="expired-logout-family",
        expires_at=now - timedelta(days=1),
        )

    db_session.add(token_record)
    db_session.commit()

    response = client.post(
        "/api/auth/logout",
        json={
            "refresh_token": expired_token
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_logout_rejects_access_token(client):
    now = datetime.now(timezone.utc)
    
    access_token = jwt.encode(
        {
            "sub": 1,
            "role": "user",
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    response = client.post(
        "/api/auth/logout",
        json={
            "refresh_token": access_token
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_logout_rejects_already_revoked_refresh_token(client, db_session):
    user = create_test_user(db_session)

    refresh_token = create_and_store_refresh_token(
        db=db_session,
        user_id=user.id,
    )
    db_session.commit()

    # First Logout
    first_response = client.post(
        "/api/auth/logout",
        json={
            "refresh_token": refresh_token
        },
    )
    assert first_response.status_code == 204

    # Secod logout suing same token.
    second_response = client.post(
        "/api/auth/logout",
        json={
            "refresh_token": refresh_token
        },
    )
    assert second_response.status_code == 401
    assert second_response.json()["detail"] == "Refresh token has already been revoked."