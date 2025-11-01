# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db
from app.auth import get_current_user
import uuid

# ✅ Base SQLite pour tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Override DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ✅ Override AUTH (simulate admin)
def override_get_current_user():
    class TestUser:
        id = 999
        nom = "Admin Test"
        email = "admin@test.com"
        type = "admin"
        equipe = "Dev"
    return TestUser()

app.dependency_overrides[get_current_user] = override_get_current_user

# ✅ Reset DB before each test
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

# ✅ Fixture client FastAPI
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# ✅ Fixture create user
@pytest.fixture
def create_test_user(client):
    unique_email = f"user_{uuid.uuid4().hex}@test.com"
    user_data = {
        "nom": "TestUser",
        "email": unique_email,
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    }
    r = client.post("/utilisateurs/", json=user_data)
    assert r.status_code == 200, r.text
    return r.json()
