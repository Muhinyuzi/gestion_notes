# app/tests/test_router_utilisateurs.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.auth import get_current_user
from app.schemas.schemas import UtilisateurCreate

# ✅ DB test
engine = create_engine("sqlite:///./test_router.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Override DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ✅ Simulated Admin User
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

def override_get_current_user():
    return FakeAdmin()

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

client = TestClient(app)

# -------------------------------------------
# ✅ TESTS
# -------------------------------------------

def test_create_user_router():
    data = {
        "nom": "TestUser",
        "email": "router@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    }
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200
    res = r.json()
    assert res["email"] == "router@test.com"

def test_list_users_router():
    # create one user
    client.post("/utilisateurs/", json={
        "nom": "UserA",
        "email": "usera@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })

    r = client.get("/utilisateurs/")
    assert r.status_code == 200

    data = r.json()
    assert "users" in data
    assert len(data["users"]) == 1  # should be one user created

def test_get_user_detail_router():
    r = client.post("/utilisateurs/", json={
        "nom": "UserB",
        "email": "userb@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 200
    assert r.json()["email"] == "userb@test.com"

def test_update_user_router():
    r = client.post("/utilisateurs/", json={
        "nom": "UserC",
        "email": "userc@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.put(f"/utilisateurs/{user_id}", json={
        "nom": "UpdatedUser",
        "email": "userc@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })

    assert r.status_code == 200
    assert r.json()["nom"] == "UpdatedUser"

def test_delete_user_router():
    r = client.post("/utilisateurs/", json={
        "nom": "UserD",
        "email": "userd@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.delete(f"/utilisateurs/{user_id}")
    assert r.status_code == 204

    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 404
