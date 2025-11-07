# app/tests/test_service_utilisateurs.py
import pytest
from starlette.background import BackgroundTasks
from app.tests.conftest import TestingSessionLocal
from app.models.utilisateur import Utilisateur
from app.services.utilisateurs import (
    create_user_service,
    list_users_service,
    get_user_detail_service,
    update_user_service,
    delete_user_service
)
from fastapi import HTTPException


# --------------------------------------------------------
# 🔸 Fake admin pour autorisation
# --------------------------------------------------------
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

fake_admin = FakeAdmin()


# --------------------------------------------------------
# 🔹 Fixture pour session DB de test
# --------------------------------------------------------
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    yield db
    db.close()


# --------------------------------------------------------
# 🔹 Test création utilisateur
# --------------------------------------------------------
def test_create_user_service(db_session):
    background_tasks = BackgroundTasks()  # ✅ ajouté
    user_data = type("UserData", (), {
        "nom": "Alice",
        "email": "alice@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev",
        "poste": None,
        "telephone": None,
        "adresse": None,
        "date_embauche": None
    })()

    user = create_user_service(user_data, db_session, current_user=fake_admin, background_tasks=background_tasks)
    assert user.email == "alice@test.com"
    assert user.nom == "Alice"


# --------------------------------------------------------
# 🔹 Test email déjà utilisé
# --------------------------------------------------------
def test_create_user_email_duplicate(db_session):
    background_tasks = BackgroundTasks()
    u = Utilisateur(nom="Dup", email="dup@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()

    user_data = type("UserData", (), {
        "nom": "Dup2",
        "email": "dup@test.com",
        "mot_de_passe": "12345678",
        "type": "user",
        "equipe": "Dev",
        "poste": None,
        "telephone": None,
        "adresse": None,
        "date_embauche": None
    })()

    with pytest.raises(HTTPException) as excinfo:
        create_user_service(user_data, db_session, current_user=fake_admin, background_tasks=background_tasks)

    assert excinfo.value.status_code == 400
    assert "Un utilisateur avec cet email existe déjà." in excinfo.value.detail


# --------------------------------------------------------
# 🔹 Test listage utilisateurs (corrigé)
# --------------------------------------------------------
def test_list_users_service(db_session):
    u = Utilisateur(nom="TestUser", email="testuser@test.com", mot_de_passe="12345678", type="user", equipe="QA")
    db_session.add(u)
    db_session.commit()

    result = list_users_service("", "", "", "", "date_desc", 1, 10, db_session, fake_admin)

    assert isinstance(result, dict)
    assert "users" in result
    assert isinstance(result["users"], list)
    assert result["total"] >= 1


# --------------------------------------------------------
# 🔹 Test détail utilisateur
# --------------------------------------------------------
def test_get_user_detail_service(db_session):
    u = Utilisateur(nom="Bob", email="bob@test.com", mot_de_passe="12345678", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    user = get_user_detail_service(u.id, db_session, fake_admin)
    assert user.id == u.id
    assert user.nom == "Bob"


# --------------------------------------------------------
# 🔹 Test mise à jour utilisateur
# --------------------------------------------------------
def test_update_user_service(db_session):
    u = Utilisateur(nom="Charlie", email="charlie@test.com", mot_de_passe="12345678", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    updated = update_user_service(u.id, {"nom": "Charles"}, db_session, fake_admin)
    assert updated.nom == "Charles"


# --------------------------------------------------------
# 🔹 Test suppression utilisateur
# --------------------------------------------------------
def test_delete_user_service(db_session):
    u = Utilisateur(nom="David", email="david@test.com", mot_de_passe="12345678", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    delete_user_service(u.id, db_session, fake_admin)
    assert db_session.query(Utilisateur).count() == 0
