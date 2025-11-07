import os
import uuid
import atexit
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.main import app
from app.db import Base, get_db
from app import emails
from app.models.utilisateur import Utilisateur
from app.auth import get_current_user
from app.config import settings


# ==========================================================
# ⚙️ CONFIGURATION GLOBALE
# ==========================================================
os.environ["TESTING"] = "1"

# Base SQLite en mémoire partagée
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
# 🚫 Blocage des envois d’e-mails réels
# ==========================================================
@pytest.fixture(autouse=True)
def disable_email_sending(monkeypatch):
    monkeypatch.setattr(emails, "send_activation_email", AsyncMock())
    monkeypatch.setattr(emails, "send_registration_email", AsyncMock())
    monkeypatch.setattr(emails, "send_reset_password_email", AsyncMock())


# ==========================================================
# 🔁 Override des dépendances FastAPI
# ==========================================================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Mémoire utilisateur de test
current_test_user = {}


# ==========================================================
# 🧩 Fonction de synchronisation DB
# ==========================================================
def ensure_user_in_db(session, user_dict):
    """S'assure que l'utilisateur override existe réellement en base."""
    db_user = session.query(Utilisateur).filter(Utilisateur.email == user_dict["email"]).first()
    if not db_user:
        db_user = Utilisateur(
            nom=user_dict.get("nom", "Test User"),
            email=user_dict["email"],
            mot_de_passe="12345678",
            type=user_dict.get("type", "user"),
            equipe=user_dict.get("equipe", "Dev"),
            is_active=True,
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def override_get_current_user():
    """Retourne un utilisateur actif depuis current_test_user, toujours présent en DB."""
    session = TestingSessionLocal()

    if current_test_user:
        db_user = ensure_user_in_db(session, current_test_user)
        return db_user

    # Fallback : admin par défaut
    fallback_admin = {
        "nom": "Admin Test",
        "email": "admin@test.com",
        "type": "admin",
        "equipe": "Dev",
    }
    db_admin = ensure_user_in_db(session, fallback_admin)
    return db_admin


app.dependency_overrides[get_current_user] = override_get_current_user

# Cas où d'autres routeurs importent leur propre dépendance
try:
    from app.routers.login import get_current_user as login_dep
    app.dependency_overrides[login_dep] = override_get_current_user
except Exception:
    pass


# ==========================================================
# 🧹 Réinitialisation complète de la base avant chaque test
# ==========================================================
@pytest.fixture(autouse=True)
def reset_db():
    """Réinitialise complètement la base avant chaque test (isolation complète)."""
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
# 🧪 Client FastAPI
# ==========================================================
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ==========================================================
# 👤 Fixtures utilitaires : création d’utilisateurs
# ==========================================================
@pytest.fixture
def create_test_user(client):
    """Crée un utilisateur admin pour tests"""
    data = {
        "nom": f"Admin_{uuid.uuid4().hex[:6]}",
        "email": f"a_{uuid.uuid4().hex}@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev",
    }
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200, f"Erreur création admin: {r.text}"
    user = r.json()
    user["is_active"] = True
    current_test_user.update(user)
    return user


@pytest.fixture
def create_test_user_non_admin(client):
    """Crée un utilisateur normal pour tests"""
    data = {
        "nom": f"User_{uuid.uuid4().hex[:6]}",
        "email": f"u_{uuid.uuid4().hex}@test.com",
        "mot_de_passe": "12345678",
        "type": "user",
        "equipe": "Dev",
    }
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200, f"Erreur création user: {r.text}"
    user = r.json()
    user["is_active"] = True
    current_test_user.update(user)
    return user


# ==========================================================
# 👥 Clients déjà authentifiés
# ==========================================================
@pytest.fixture
def admin_client(client, create_test_user):
    current_test_user.update(create_test_user)
    return client


@pytest.fixture
def user_client(client, create_test_user_non_admin):
    current_test_user.update(create_test_user_non_admin)
    return client


# ==========================================================
# 🧩 Activation utilisateur simulée
# ==========================================================
def activate_user_via_token(client, email: str):
    """Active un utilisateur via le vrai endpoint /auth/activate/{token}"""
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
    assert r.status_code == 200, f"Échec activation via token: {r.text}"


# ==========================================================
# 🔍 Outil debug
# ==========================================================
def debug_dump_db(session):
    """Affiche toutes les tables et leur contenu"""
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
