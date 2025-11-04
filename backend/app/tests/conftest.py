# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db
import uuid
import os

os.environ["TESTING"] = "1"

# ✅ In-memory SQLite partagé
TEST_DATABASE_URL = "sqlite:///file:memdb1?mode=memory&cache=shared"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ✅ Override DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# ✅ Gestion user dynamique pour tests
current_test_user = {}

def override_get_current_user():
    if current_test_user.get("id"):
        return current_test_user
    return type("User", (), {
        "id": 999, "nom": "Admin Test", "email": "admin@test.com",
        "type": "admin", "equipe": "Dev"
    })()

from app.auth import get_current_user
app.dependency_overrides[get_current_user] = override_get_current_user

# ✅ IMPORTANT : override aussi login router
try:
    from app.routers.login import get_current_user as login_dep
    app.dependency_overrides[login_dep] = override_get_current_user
except Exception:
    pass


# ✅ Reset DB before each test
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        try:
            conn.execute(text("DELETE FROM sqlite_sequence"))
        except Exception:
            pass

    current_test_user.clear()
    yield


# ✅ Test client
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ✅ Create user via API + activate it
@pytest.fixture
def create_test_user(client):
    data = {
        "nom": f"User_{uuid.uuid4().hex[:6]}",
        "email": f"u_{uuid.uuid4().hex}@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    }

    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200

    user = r.json()
    current_test_user.update(user)
    return user


# ✅ Debug function: print tables + content
def debug_dump_db(session):
    inspector = inspect(session.bind)
    print("\n---- DB TABLES ----")
    for table in inspector.get_table_names():
        rows = session.execute(text(f"SELECT * FROM {table}")).fetchall()
        print(f"\n📌 {table} ({len(rows)} rows)")
        for row in rows:
            print(dict(row))


__all__ = ["engine", "TestingSessionLocal", "debug_dump_db", "current_test_user"]
