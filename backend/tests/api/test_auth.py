# backend/tests/api/test_auth.py
from fastapi.testclient import TestClient

def test_login(client: TestClient):
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123",
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_login_incorrect_password(client: TestClient):
    login_data = {
        "username": "test@example.com",
        "password": "WrongPassword",
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401

def test_get_me(client: TestClient, user_token_headers):
    response = client.get("/api/users/me", headers=user_token_headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "test@example.com"
    assert user["role"] == "student"

def test_register_user(client: TestClient):
    user_data = {
        "email": "newuser@example.com",
        "password": "NewUserPass123",
        "first_name": "New",
        "last_name": "User",
        "role": "student"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["email"] == user_data["email"]
    assert created_user["role"] == user_data["role"]