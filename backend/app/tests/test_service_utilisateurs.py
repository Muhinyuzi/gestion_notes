# app/tests/test_service_utilisateurs.py
import pytest
from starlette.background import BackgroundTasks
from fastapi import HTTPException
from app.tests.conftest import TestingSessionLocal
from app.models.utilisateur import Utilisateur
from app.services.utilisateurs import (
    create_user_service,
    list_users_service,
    get_user_detail_service,
    update_user_service,
    delete_user_service,
)

# --------------------------------------------------------
# 🔸 Fake admin & user pour tests d’autorisations
# --------------------------------------------------------
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

class FakeUser:
    id = 2
    type = "user"
    equipe = "Support"

fake_admin = FakeAdmin()
fake_user = FakeUser()

# --------------------------------------------------------
# 🔹 Fixture pour session DB isolée
# --------------------------------------------------------
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()

# --------------------------------------------------------
# 🔹 Création utilisateur (OK)
# --------------------------------------------------------
def test_create_user_service(db_session):
    background_tasks = BackgroundTasks()
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
# 🔹 Création refusée pour non-admin
# --------------------------------------------------------
def test_create_user_unauthorized(db_session):
    background_tasks = BackgroundTasks()
    user_data = type("UserData", (), {
        "nom": "NoAuth",
        "email": "noauth@test.com",
        "mot_de_passe": "12345678",
        "type": "user",
        "equipe": "Ops",
        "poste": None,
        "telephone": None,
        "adresse": None,
        "date_embauche": None
    })()
    with pytest.raises(HTTPException) as excinfo:
        create_user_service(user_data, db_session, current_user=fake_user, background_tasks=background_tasks)
    assert excinfo.value.status_code == 403
    assert "Seuls les administrateurs" in excinfo.value.detail

# --------------------------------------------------------
# 🔹 Email déjà utilisé (erreur 400)
# --------------------------------------------------------
def test_create_user_email_duplicate(db_session):
    background_tasks = BackgroundTasks()
    existing = Utilisateur(nom="Dup", email="dup@test.com", mot_de_passe="xxx", type="user")
    db_session.add(existing)
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
# 🔹 Liste des utilisateurs
# --------------------------------------------------------
def test_list_users_service(db_session):
    u = Utilisateur(nom="TestUser", email="testuser@test.com", mot_de_passe="12345678", type="user", equipe="QA")
    db_session.add(u)
    db_session.commit()
    result = list_users_service("", "", "", "", "date_desc", 1, 10, db_session, fake_admin)
    assert isinstance(result, dict)
    assert "users" in result
    assert result["total"] >= 1

# --------------------------------------------------------
# 🔹 Liste refusée si non admin
# --------------------------------------------------------
def test_list_users_unauthorized(db_session):
    with pytest.raises(HTTPException) as excinfo:
        list_users_service("", "", "", "", "date_desc", 1, 10, db_session, fake_user)
    assert excinfo.value.status_code == 403

# --------------------------------------------------------
# 🔹 Détail utilisateur
# --------------------------------------------------------
def test_get_user_detail_service(db_session):
    u = Utilisateur(nom="Bob", email="bob@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    user = get_user_detail_service(u.id, db_session, fake_admin)
    assert user.id == u.id
    assert user.nom == "Bob"

# --------------------------------------------------------
# 🔹 Détail utilisateur non trouvé
# --------------------------------------------------------
def test_get_user_detail_not_found(db_session):
    with pytest.raises(HTTPException) as excinfo:
        get_user_detail_service(9999, db_session, fake_admin)
    assert excinfo.value.status_code == 404

# --------------------------------------------------------
# 🔹 Mise à jour utilisateur (OK)
# --------------------------------------------------------
def test_update_user_service(db_session):
    u = Utilisateur(nom="Charlie", email="charlie@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    updated = update_user_service(u.id, {"nom": "Charles"}, db_session, fake_admin)
    assert updated.nom == "Charles"

# --------------------------------------------------------
# 🔹 Mise à jour refusée pour non admin
# --------------------------------------------------------
def test_update_user_unauthorized(db_session):
    u = Utilisateur(nom="NormalUser", email="normal@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    with pytest.raises(HTTPException) as excinfo:
        update_user_service(u.id, {"type": "admin"}, db_session, fake_user)
    assert excinfo.value.status_code == 403

# --------------------------------------------------------
# 🔹 Mise à jour d’un email déjà existant
# --------------------------------------------------------
def test_update_user_email_duplicate(db_session):
    user1 = Utilisateur(nom="One", email="one@test.com", mot_de_passe="123", type="user")
    user2 = Utilisateur(nom="Two", email="two@test.com", mot_de_passe="123", type="user")
    db_session.add_all([user1, user2])
    db_session.commit()
    with pytest.raises(HTTPException) as excinfo:
        update_user_service(user2.id, {"email": "one@test.com"}, db_session, fake_admin)
    assert excinfo.value.status_code == 400
    assert "déjà utilisé" in excinfo.value.detail

# --------------------------------------------------------
# 🔹 Suppression utilisateur (OK)
# --------------------------------------------------------
def test_delete_user_service(db_session):
    u = Utilisateur(nom="David", email="david@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    delete_user_service(u.id, db_session, fake_admin)
    assert db_session.query(Utilisateur).count() == 0

# --------------------------------------------------------
# 🔹 Suppression refusée pour non admin
# --------------------------------------------------------
def test_delete_user_unauthorized(db_session):
    u = Utilisateur(nom="Eve", email="eve@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    with pytest.raises(HTTPException) as excinfo:
        delete_user_service(u.id, db_session, fake_user)
    assert excinfo.value.status_code == 403

# --------------------------------------------------------
# 🔹 Suppression d’un utilisateur inexistant
# --------------------------------------------------------
def test_delete_user_not_found(db_session):
    with pytest.raises(HTTPException) as excinfo:
        delete_user_service(9999, db_session, fake_admin)
    assert excinfo.value.status_code == 404
