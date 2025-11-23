import io
import pytest
from datetime import datetime
from starlette.background import BackgroundTasks
from fastapi import HTTPException, UploadFile
from app.tests.conftest import TestingSessionLocal
from app.models.utilisateur import Utilisateur
from app.services.utilisateurs import (
    create_user_service,
    list_users_service,
    get_user_detail_service,
    update_user_service,
    delete_user_service,
    upload_avatar_service,
    get_avatar_service
)

# =========================================================
# 🔸 Fake utilisateurs
# =========================================================
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

# =========================================================
# 🔹 Fixture DB
# =========================================================
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()

# =========================================================
# 🔹 Création utilisateur
# =========================================================
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
    user = create_user_service(user_data, db_session, fake_admin, background_tasks)
    assert user.email == "alice@test.com"
    assert user.is_active is False

def test_create_user_unauthorized(db_session):
    background_tasks = BackgroundTasks()
    user_data = type("UserData", (), {
        "nom": "NoAuth",
        "email": "noauth@test.com",
        "mot_de_passe": "12345678",
        "type": "user",
        "equipe": "Ops"
    })()
    with pytest.raises(HTTPException) as excinfo:
        create_user_service(user_data, db_session, fake_user, background_tasks)
    assert excinfo.value.status_code == 403

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
        "equipe": "Dev"
    })()
    with pytest.raises(HTTPException):
        create_user_service(user_data, db_session, fake_admin, background_tasks)

# =========================================================
# 🔹 Listing
# =========================================================
def test_list_users_service(db_session):
    for i in range(3):
        db_session.add(Utilisateur(nom=f"User{i}", email=f"user{i}@test.com", mot_de_passe="123", type="user", equipe="QA"))
    db_session.commit()

    result = list_users_service("", "", "", "", "nom_asc", 1, 10, db_session, fake_admin)
    assert isinstance(result, dict)
    assert result["total"] >= 3
    assert any("user0" in u.email for u in result["users"])

def test_list_users_with_filter(db_session):
    db_session.add(Utilisateur(nom="Filtered", email="f@test.com", mot_de_passe="123", type="admin", equipe="Dev"))
    db_session.commit()
    res = list_users_service("Filtered", "", "", "", "date_desc", 1, 5, db_session, fake_admin)
    assert len(res["users"]) == 1

def test_list_users_unauthorized(db_session):
    with pytest.raises(HTTPException):
        list_users_service("", "", "", "", "nom_asc", 1, 10, db_session, fake_user)

# =========================================================
# 🔹 Détail
# =========================================================
def test_get_user_detail_service(db_session):
    u = Utilisateur(nom="Bob", email="bob@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    res = get_user_detail_service(u.id, db_session, fake_admin)
    assert res.email == "bob@test.com"

def test_get_user_detail_not_found(db_session):
    with pytest.raises(HTTPException):
        get_user_detail_service(9999, db_session, fake_admin)

def test_get_user_detail_unauthorized(db_session):
    u = Utilisateur(nom="Zoe", email="zoe@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    with pytest.raises(HTTPException):
        get_user_detail_service(u.id, db_session, fake_user)

# =========================================================
# 🔹 Mise à jour
# =========================================================
def test_update_user_service(db_session):
    u = Utilisateur(nom="Charlie", email="charlie@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    updated = update_user_service(u.id, {"nom": "Charles"}, db_session, fake_admin)
    assert updated.nom == "Charles"

def test_update_user_self_allowed(db_session):
    u = Utilisateur(id=2, nom="Self", email="self@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    updated = update_user_service(u.id, {"adresse": "Rue Test"}, db_session, fake_user)
    assert updated.adresse == "Rue Test"

def test_update_user_email_duplicate(db_session):
    user1 = Utilisateur(nom="One", email="one@test.com", mot_de_passe="123", type="user")
    user2 = Utilisateur(nom="Two", email="two@test.com", mot_de_passe="123", type="user")
    db_session.add_all([user1, user2])
    db_session.commit()
    with pytest.raises(HTTPException):
        update_user_service(user2.id, {"email": "one@test.com"}, db_session, fake_admin)

def test_update_user_unauthorized(db_session):
    u = Utilisateur(nom="Normal", email="n@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    with pytest.raises(HTTPException):
        update_user_service(u.id, {"type": "admin"}, db_session, fake_user)

# =========================================================
# 🔹 Suppression
# =========================================================
def test_delete_user_service(db_session):
    u = Utilisateur(nom="David", email="david@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    delete_user_service(u.id, db_session, fake_admin)
    assert db_session.query(Utilisateur).count() == 0

def test_delete_user_unauthorized(db_session):
    u = Utilisateur(nom="Eve", email="eve@test.com", mot_de_passe="123", type="user")
    db_session.add(u)
    db_session.commit()
    with pytest.raises(HTTPException):
        delete_user_service(u.id, db_session, fake_user)

def test_delete_user_not_found(db_session):
    with pytest.raises(HTTPException):
        delete_user_service(9999, db_session, fake_admin)

# =========================================================
# 🔹 Upload Avatar
# =========================================================
@pytest.mark.asyncio
async def test_upload_avatar_valid(tmp_path, db_session):
    user = Utilisateur(nom="Pic", email="pic@test.com", mot_de_passe="123", type="user")
    db_session.add(user)
    db_session.commit()
    fake_file = UploadFile(filename="avatar.jpg", file=io.BytesIO(b"fakeimagedata"))
    res = await upload_avatar_service(user.id, fake_file, db_session)
    assert "avatar_url" in res

@pytest.mark.asyncio
async def test_upload_avatar_invalid_format(db_session):
    user = Utilisateur(nom="BadPic", email="bad@test.com", mot_de_passe="123", type="user")
    db_session.add(user)
    db_session.commit()
    fake_file = UploadFile(filename="malicious.exe", file=io.BytesIO(b"123"))
    with pytest.raises(HTTPException):
        await upload_avatar_service(user.id, fake_file, db_session)

@pytest.mark.asyncio
async def test_get_avatar_not_found(db_session):
    user = Utilisateur(nom="Ghost", email="ghost@test.com", mot_de_passe="123", type="user", avatar_url=None)
    db_session.add(user)
    db_session.commit()
    with pytest.raises(HTTPException):
        await get_avatar_service(user.id, db_session)


@pytest.mark.asyncio
async def test_upload_avatar_too_large(db_session):
    """🚫 Upload refusé : fichier > 2 Mo"""
    user = Utilisateur(nom="BigFile", email="big@test.com", mot_de_passe="123", type="user")
    db_session.add(user)
    db_session.commit()

    # Simule un fichier de 3 Mo
    big_content = io.BytesIO(b"a" * (3 * 1024 * 1024))
    fake_file = UploadFile(filename="photo.jpg", file=big_content)

    with pytest.raises(HTTPException) as excinfo:
        await upload_avatar_service(user.id, fake_file, db_session)

    assert excinfo.value.status_code == 400
    assert "trop volumineux" in excinfo.value.detail


@pytest.mark.asyncio
async def test_upload_avatar_png_valid(db_session):
    """✅ Upload valide avec extension PNG"""
    user = Utilisateur(nom="Pic2", email="pic2@test.com", mot_de_passe="123", type="user")
    db_session.add(user)
    db_session.commit()

    fake_file = UploadFile(filename="avatar.png", file=io.BytesIO(b"fakepngdata"))
    res = await upload_avatar_service(user.id, fake_file, db_session)

    assert "avatar_url" in res
    assert res["avatar_url"].endswith(".png")


@pytest.mark.asyncio
async def test_get_avatar_existing(tmp_path, db_session):
    """✅ Récupération d’un avatar existant (FileResponse)"""
    user = Utilisateur(nom="AvatarUser", email="ava@test.com", mot_de_passe="123", type="user")
    db_session.add(user)
    db_session.commit()

    # On crée un faux fichier avatar
    avatar_path = tmp_path / "avatar.jpg"
    avatar_path.write_bytes(b"fakeimagedata")

    user.avatar_url = f"http://127.0.0.1:8000/{avatar_path}"
    db_session.commit()

    response = await get_avatar_service(user.id, db_session)
    assert response.status_code == 200
    assert "image" in response.media_type
