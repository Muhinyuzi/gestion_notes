# app/tests/test_service_utilisateurs.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models.utilisateur import Utilisateur
from app.services.utilisateurs import (
    create_user_service,
    list_users_service,
    get_user_detail_service,
    update_user_service,
    delete_user_service
)
from app.schemas.schemas import UtilisateurCreate

# ✅ DB test SQLite en mémoire (rapide)
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)

# ✅ Faux utilisateur admin injecté
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

fake_admin = FakeAdmin()

def create_test_user(db):
    user_data = UtilisateurCreate(
        nom="TestUser",
        email="test@example.com",
        mot_de_passe="1234",
        type="admin",
        equipe="Dev"
    )
    return create_user_service(user_data, db, fake_admin)

def test_create_user_service(db):
    user = create_test_user(db)
    assert user.email == "test@example.com"

def test_list_users_service(db):
    create_test_user(db)
    result = list_users_service(None, None, None, None, None, 1, 20, db, fake_admin)
    assert result["total"] == 1
    assert len(result["users"]) == 1

def test_get_user_detail_service(db):
    user = create_test_user(db)
    u = get_user_detail_service(user.id, db, fake_admin)
    assert u.email == "test@example.com"

def test_update_user_service(db):
    user = create_test_user(db)
    update_data = UtilisateurCreate(
        nom="Updated",
        email="test@example.com",
        mot_de_passe="abcd",
        type="admin",
        equipe="Dev"
    )
    updated = update_user_service(user.id, update_data, db, fake_admin)
    assert updated.nom == "Updated"

def test_delete_user_service(db):
    user = create_test_user(db)
    delete_user_service(user.id, db, fake_admin)
    assert db.query(Utilisateur).count() == 0
