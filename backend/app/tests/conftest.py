# app/tests/conftest.py

import os
import uuid
import atexit
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from fastapi import Request
from jose import jwt

from app.main import app
from app.db import Base, get_db
from app import emails
from app.models.utilisateur import Utilisateur
from app.auth import hash_password, get_current_user as auth_dep
from app.config import settings


# ==========================================================
# ✅ MODE TEST
# ==========================================================
os.environ["TESTING"] = "1"


# ==========================================================
# ✅ BASE SQLITE EN MÉMOIRE
# ==========================================================
TEST_DATABASE_URL = f"sqlite:///file:test_db_{uuid.uuid4().hex}?mode=memory&cache=shared"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True},
    pool_pre_ping=True,
    echo=False,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@atexit.register
def cleanup_test_db():
    print("🧹 Test DB cleaned up.")


# ==========================================================
# ✅ MOCK EMAILS
# ==========================================================
@pytest.fixture(autouse=True)
def disable_email_sending(monkeypatch):
    monkeypatch.setattr(emails, "send_activation_email", AsyncMock())
    monkeypatch.setattr(emails, "send_registration_email", AsyncMock())
    monkeypatch.setattr(emails, "send_reset_password_email", AsyncMock())


# ==========================================================
# ✅ OVERRIDE DB
# ==========================================================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# ==========================================================
# ✅ TEMP ADMIN (pour création utilisateurs)
# ==========================================================
def _temp_admin():
    return Utilisateur(
        id=999,
        nom="Temp Admin",
        email="tempadmin@test.com",
        type="admin",
        equipe="Dev",
        mot_de_passe=hash_password("12345678"),
        is_active=True,
    )


def override_as_temp_admin():
    """✅ Version propre (sans lambda) pour éviter le bug Query('_')"""
    return _temp_admin()


# ==========================================================
# ✅ MÉMOIRE POUR STOCKER L’UTILISATEUR COURANT
# ==========================================================
current_test_user = {}


def ensure_user_in_db(session, user_dict):
    """S’assure que l’utilisateur existe en DB, sinon le crée."""
    db_user = session.query(Utilisateur).filter_by(email=user_dict["email"]).first()
    if not db_user:
        db_user = Utilisateur(
            nom=user_dict.get("nom", "Test User"),
            email=user_dict["email"],
            mot_de_passe=hash_password(user_dict.get("mot_de_passe", "12345678")),
            type=user_dict.get("type", "user"),
            equipe=user_dict.get("equipe", "Dev"),
            is_active=True,
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # ✅ important : si type admin demandé, on force
    if user_dict.get("type") == "admin" and db_user.type != "admin":
        db_user.type = "admin"
        session.commit()

    return db_user


# ==========================================================
# ✅ OVERRIDE AUTH RÉEL (lit le JWT)
# ==========================================================
def override_get_current_user(request: Request):
    session = TestingSessionLocal()

    # ✅ 1. lire Authorization: Bearer TOKEN
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")  # ✅ CORRIGÉ : sub = ID et pas email !

            if user_id:
                db_user = session.query(Utilisateur).filter_by(id=user_id).first()
                if db_user:
                    return db_user

        except Exception:
            pass

    # ✅ 2. sinon fallback test_user (créé par fixture)
    if current_test_user:
        return ensure_user_in_db(session, current_test_user)

    # ✅ 3. sinon fallback admin complet
    return ensure_user_in_db(
        session,
        {
            "nom": "Admin Test",
            "email": "admin@test.com",
            "type": "admin",
            "equipe": "Dev",
        },
    )

# ✅ override auth global
app.dependency_overrides[auth_dep] = override_get_current_user


# ✅ override des modules
for module_path in [
    "app.routers.login",
    "app.routers.utilisateurs",
    "app.routers.notes",
    "app.routers.commentaires",
    "app.routers.change_password",
]:
    try:
        module = __import__(module_path, fromlist=["get_current_user"])
        app.dependency_overrides[module.get_current_user] = override_get_current_user
    except Exception:
        pass


# ==========================================================
# ✅ RESET DB ENTRE CHAQUE TEST
# ==========================================================
@pytest.fixture(autouse=True)
def reset_db():
    global engine, TestingSessionLocal

    engine.dispose()
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False, "uri": True},
        pool_pre_ping=True,
        echo=False,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    current_test_user.clear()

    yield


# ==========================================================
# ✅ CLIENT FASTAPI
# ==========================================================
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ==========================================================
# ✅ FIXTURES UTILISATEURS (avec admin temporaire propre)
# ==========================================================
@pytest.fixture
def create_test_user(client):
    """Créer un admin"""

    # ✅ permet de bypasser la restriction admin
    app.dependency_overrides[auth_dep] = override_as_temp_admin

    data = {
        "nom": f"Admin_{uuid.uuid4().hex[:6]}",
        "email": f"a_{uuid.uuid4().hex}@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev",
    }

    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200, r.text

    #user = r.json()
    data = r.json()
    user = data.get("data", data)
    current_test_user.update(user)

    # ✅ restore vrai auth
    app.dependency_overrides[auth_dep] = override_get_current_user
    return user


@pytest.fixture
def create_test_user_non_admin(client):
    """Créer un utilisateur simple"""

    app.dependency_overrides[auth_dep] = override_as_temp_admin

    data = {
        "nom": f"User_{uuid.uuid4().hex[:6]}",
        "email": f"u_{uuid.uuid4().hex}@test.com",
        "mot_de_passe": "12345678",
        "type": "user",
        "equipe": "Dev",
    }

    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200, r.text

    #user = r.json()
    data = r.json()
    user = data.get("data", data)
    current_test_user.update(user)

    app.dependency_overrides[auth_dep] = override_get_current_user
    return user


# ==========================================================
# ✅ CLIENTS AUTH
# ==========================================================
@pytest.fixture
def admin_client(client, create_test_user):
    return client

@pytest.fixture
def user_client(client, create_test_user_non_admin):
    return client


# ==========================================================
# ✅ ACTIVATION
# ==========================================================
def activate_user_via_token(client, email: str):
    token = jwt.encode(
        {
            "sub": email,
            "type": "activation",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    r = client.get(f"/auth/activate/{token}")
    assert r.status_code == 200, f"Activation échouée: {r.text}"


# ==========================================================
# ✅ DEBUG DB
# ==========================================================
def debug_dump_db(session):
    inspector = inspect(session.bind)
    print("\n---- DB TABLES ----")
    for table in inspector.get_table_names():
        rows = session.execute(text(f"SELECT * FROM {table}")).fetchall()
        print(f"\n📌 {table} ({len(rows)} rows)")
        for row in rows:
            print(dict(row))


__all__ = [
    "engine",
    "TestingSessionLocal",
    "debug_dump_db",
    "current_test_user",
    "admin_client",
    "user_client",
    "activate_user_via_token",
]
