# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings
from app.services import user_service

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create test database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def test_user(db):
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student"
    }

    user = user_service.get_by_email(db, email=user_data["email"])
    if not user:
        user = user_service.create(
            db,
            obj_in=user_data
        )

    return user

@pytest.fixture(scope="module")
def test_instructor(db):
    user_data = {
        "email": "instructor@example.com",
        "password": "InstructorPass123",
        "first_name": "Test",
        "last_name": "Instructor",
        "role": "instructor"
    }

    user = user_service.get_by_email(db, email=user_data["email"])
    if not user:
        user = user_service.create(
            db,
            obj_in=user_data
        )

    return user

@pytest.fixture(scope="module")
def test_admin(db):
    user_data = {
        "email": "admin@example.com",
        "password": "AdminPass123",
        "first_name": "Test",
        "last_name": "Admin",
        "role": "admin"
    }

    user = user_service.get_by_email(db, email=user_data["email"])
    if not user:
        user = user_service.create(
            db,
            obj_in=user_data
        )

    return user

@pytest.fixture(scope="module")
def user_token_headers(client, test_user):
    login_data = {
        "username": test_user.email,
        "password": "TestPassword123",
    }
    response = client.post("/api/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="module")
def instructor_token_headers(client, test_instructor):
    login_data = {
        "username": test_instructor.email,
        "password": "InstructorPass123",
    }
    response = client.post("/api/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="module")
def admin_token_headers(client, test_admin):
    login_data = {
        "username": test_admin.email,
        "password": "AdminPass123",
    }
    response = client.post("/api/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}