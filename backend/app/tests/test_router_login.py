# app/tests/test_router_login.py
import pytest
from app.tests.conftest import TestingSessionLocal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success(create_test_user):
    # L'utilisateur est déjà créé via create_test_user fixture
    email = create_test_user["email"]
    password = "1234"

    # FastAPI OAuth2 utilise form-data, pas JSON
    response = client.post(
        "/login",
        data={"username": email, "password": password}
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == email


def test_login_wrong_password(create_test_user):
    email = create_test_user["email"]

    response = client.post(
        "/login",
        data={"username": email, "password": "badpass"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.text.lower()


def test_login_user_not_found():
    response = client.post(
        "/login",
        data={"username": "notexist@test.com", "password": "test"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.text.lower()
