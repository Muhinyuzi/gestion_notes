# app/tests/test_router_login.py
import pytest
from app.tests.conftest import TestingSessionLocal
from fastapi.testclient import TestClient
from app.main import app
from jose import jwt
from app.config import settings

client = TestClient(app)



def test_login_success(client, create_test_user):
    email = create_test_user["email"]
    password = "12345678"

    # ✅ Activer l'utilisateur d'abord
    token = jwt.encode(
        {"sub": email, "type": "activation"},
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    r = client.get(f"/auth/activate?token={token}")
    assert r.status_code == 200

    # ✅ Login après activation
    response = client.post(
        "/login",
        data={"username": email, "password": password}
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == email


def test_login_wrong_password(client, create_test_user):
    email = create_test_user["email"]

    response = client.post(
        "/login",
        data={"username": email, "password": "badpass"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.text.lower()


def test_login_user_not_found(client):
    response = client.post(
        "/login",
        data={"username": "notexist@test.com", "password": "test"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.text.lower()